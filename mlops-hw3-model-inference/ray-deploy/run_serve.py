#!/usr/bin/env python3.10
import ray
from ray import serve
import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища з файлу .env (якщо він існує)
load_dotenv()

# Ініціалізація Ray з середовищем виконання на рівні завдання
ray.init(
    address="ray://localhost:10001",
    runtime_env={
        "working_dir": ".",
        "pip": [
            "tensorflow",
            "ultralytics",
            "wandb", 
            "python-dotenv",
            "opencv-python-headless",
            "matplotlib",
            "seaborn",
            "scikit-learn",
        ],
        "env_vars": {
            "OPENCV_IO_ENABLE_OPENEXR": "0",
            "OPENCV_IO_ENABLE_JASPER": "0", 
            "QT_QPA_PLATFORM": "offscreen",
            "MPLBACKEND": "Agg",
            # Передаємо wandb змінні середовища в Ray
            "WANDB_PROJECT": os.getenv("WANDB_PROJECT", "linear-regression-pytorch"),
            "WANDB_ENTITY": os.getenv("WANDB_ENTITY", "berejant-set-university"),
            "WANDB_MODEL_ARTIFACT": os.getenv("WANDB_MODEL_ARTIFACT", "berejant-set-university/catdog-mobilenetv2/run_n0h1n2re_model:latest"),
            "WANDB_API_KEY": os.getenv("WANDB_API_KEY", ""),
            "WANDB_MODE": os.getenv("WANDB_MODE", "online"),
            "WANDB_SILENT": "true"
        }
    }
)

# Імпорт застосунку після ініціалізації Ray
from object_detection import entrypoint

# Запуск застосунку serve
serve.run(entrypoint, name="yolo") 
