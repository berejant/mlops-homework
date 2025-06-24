import os
import wandb

wandb.require("core")

wandb_api_key = os.getenv("WANDB_API_KEY")
wandb.login(key=wandb_api_key)

run = wandb.init()

artifact = run.use_artifact('berejant-set-university/catdog-mobilenetv2/run_n0h1n2re_model:latest', type='model')
path = artifact.get_path("wandb_model.keras")
path.download('./model/')