#!/usr/bin/env python3
"""
Скрипт тренування YOLOv8n з інтеграцією Weights & Biases
Тренує модель YOLOv8n на CPU з повним відстеженням W&B та збереженням моделі
Використовує вбудовану інтеграцію YOLO W&B
"""

import os
import pandas as pd
import numpy as np
import boto3
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import wandb
from wandb.integration.keras import WandbCallback

# Constants
CSV_PATH = 'dataset/dataset.csv'
IMAGES_DIR = 'dataset/images'
IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 20

def download_image_from_s3(s3_path, local_path):
    if os.path.exists(local_path):
        return
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('MINIO_SECRET_KEY'),
        endpoint_url='http://localhost:9000'
    )
    bucket, key = s3_path.replace('s3://', '').split('/', 1)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3.download_file(bucket, key, local_path)

def prepare_images(df):
    local_paths = []
    for s3_path in tqdm(df['image']):
        # s3://catdog-dataset/Cat/10903.jpg -> dataset/images/Cat/10903.jpg
        rel_path = '/'.join(s3_path.split('/')[3:])
        local_path = os.path.join(IMAGES_DIR, rel_path)
        download_image_from_s3(s3_path, local_path)
        local_paths.append(local_path)
    return local_paths

def main():
    # Load CSV
    df = pd.read_csv(CSV_PATH)
    # Remove rows with missing image or label
    df = df.dropna(subset=['image', 'choice'])
    # Only keep Cat/Dog
    df = df[df['choice'].isin(['Cat', 'Dog'])]
    # Download images and get local paths
    print('Downloading images from S3 (if needed)...')
    df['local_path'] = prepare_images(df)
    # Map labels
    df['label'] = df['choice'].map({'Cat': 0, 'Dog': 1}).astype(str)
    # Split
    train_val, test = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    train, val = train_test_split(train_val, test_size=0.2, stratify=train_val['label'], random_state=42)
    # Data generators
    datagen = ImageDataGenerator(rescale=1./255)
    train_gen = datagen.flow_from_dataframe(
        train, x_col='local_path', y_col='label', target_size=IMG_SIZE, class_mode='binary', batch_size=BATCH_SIZE, shuffle=True)
    val_gen = datagen.flow_from_dataframe(
        val, x_col='local_path', y_col='label', target_size=IMG_SIZE, class_mode='binary', batch_size=BATCH_SIZE, shuffle=False)
    test_gen = datagen.flow_from_dataframe(
        test, x_col='local_path', y_col='label', target_size=IMG_SIZE, class_mode='binary', batch_size=BATCH_SIZE, shuffle=False)
    # Model
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    # W&B
    wandb.init(project='catdog-mobilenetv2', name='mobilenetv2-csv')
    # Callbacks
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, verbose=1)
    # Train
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=[early_stop, reduce_lr, WandbCallback()]
    )
    # Save model
    model.save('cats_dogs_classifier.keras')
    print('Model saved as cats_dogs_classifier.keras')
    # Evaluate
    loss, acc = model.evaluate(test_gen)
    print(f'Test accuracy: {acc:.4f}')
    wandb.log({'test_accuracy': acc, 'test_loss': loss})

if __name__ == '__main__':
    main() 