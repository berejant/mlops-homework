from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from tensorflow import keras
from PIL import Image
import numpy as np
import io

# Ініціалізація FastAPI
app = FastAPI()

# Load Keras model
MODEL_PATH = 'model/cat_dog_nothing_model.keras'  # Adjust path as needed
model = keras.models.load_model(MODEL_PATH)

# Class labels
CLASS_NAMES = ['cat', 'dog', 'nothing']

# Preprocessing function (adjust target size as per your model)
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))  # Change size if your model expects different
    img_array = np.array(img) / 255.0  # Normalize if model trained on normalized images
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Маршрут для передбачень
@app.post("/invocations")
def predict(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    input_tensor = preprocess_image(image_bytes)
    preds = model.predict(input_tensor)
    pred_class = CLASS_NAMES[int(np.argmax(preds))]
    confidence = float(np.max(preds))
    return JSONResponse({
        "class": pred_class,
        "confidence": confidence
    })

# Маршрут для перевірки стану сервісу
@app.get("/ping")
def ping():
    return {"status": "ok"}

# Запуск сервісу, якщо модуль запускається безпосередньо
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
