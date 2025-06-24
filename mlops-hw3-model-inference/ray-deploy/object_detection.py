import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "tensorflow", "numpy"], check=True)


import tensorflow as tf
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import requests
from PIL import Image
import numpy as np
import wandb
import os
import io

import ray
from ray import serve
from ray.serve.handle import DeploymentHandle

#serve.start(http_options={"host": "0.0.0.0", "port": 8001})

app = FastAPI()

CLASS_NAMES = ['cat', 'dog', 'nothing']

@serve.deployment(
    num_replicas=1,
    ray_actor_options={
        "num_cpus": 1,
    }
)
@serve.ingress(app)
class APIIngress:
    def __init__(self, classifier_handle) -> None:
        self.handle: DeploymentHandle = classifier_handle.options(
            use_new_handle_api=True,
        )

    @app.get("/detect")
    async def detect(self, image_url: str):
        result = await self.handle.classify.remote(image_url)
        return JSONResponse(content=result)

@serve.deployment(
    autoscaling_config={"min_replicas": 1, "max_replicas": 2},
    ray_actor_options={
        "num_cpus": 1,
    }
)
class ImageClassifier:
    def __init__(self):
        self.wandb_project = os.getenv("WANDB_PROJECT", "linear-regression-pytorch")
        self.wandb_entity = os.getenv("WANDB_ENTITY", "berejant-set-university")
        self.model_artifact_name = os.getenv("WANDB_MODEL_ARTIFACT", "berejant-set-university/catdog-mobilenetv2/run_n0h1n2re_model:latest")
        print("🤖 Initializing wandb and loading Keras model...")
        os.environ["WANDB_MODE"] = "online"
        run = wandb.init(
            project=self.wandb_project,
            entity=self.wandb_entity,
            job_type="inference",
            mode="online"
        )
        try:
            api_key = os.getenv("WANDB_API_KEY")
            if not api_key:
                raise ValueError("WANDB_API_KEY not found in environment variables")
            print(f"📥 Downloading model artifact: {self.model_artifact_name}")
            artifact = run.use_artifact(self.model_artifact_name, type='model')
            model_path = artifact.download()
            model_file = None
            for file in os.listdir(model_path):
                if file.endswith('.keras'):
                    model_file = os.path.join(model_path, file)
                    break
            if model_file is None:
                raise FileNotFoundError("No .keras model file found in the downloaded artifact")
            print(f"📁 Model file path: {model_file}")
            self.model = tf.keras.models.load_model(model_file)
            print("✅ Model loaded from wandb!")
        except Exception as e:
            print(f"❌ Failed to load model from wandb: {e}")
            print("🔄 Falling back to failback_model.keras...")
            self.model = tf.keras.models.load_model('failback_model.keras')
            print("✅ Fallback model loaded!")
        finally:
            wandb.finish()

    @staticmethod
    def preprocess_image(image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224))  # Adjust if your model expects a different size
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    async def classify(self, image_url: str):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            img_bytes = response.content
            input_tensor = self.preprocess_image(img_bytes)
            preds = self.model.predict(input_tensor)
            pred_class = CLASS_NAMES[int(np.argmax(preds))]
            confidence = float(np.max(preds))
            return {"class": pred_class, "confidence": confidence}
        except Exception as e:
            return {"error": str(e)}

entrypoint = APIIngress.bind(ImageClassifier.bind())
