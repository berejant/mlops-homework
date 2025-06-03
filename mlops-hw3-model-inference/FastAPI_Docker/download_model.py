import os
import wandb

wandb.require("core")

wandb_api_key = os.getenv("WANDB_API_KEY")
wandb.login(key=wandb_api_key)

run = wandb.init()

artifact = run.use_artifact('berejant-set-university/linear-regression-pytorch/linear_regression_model:latest', type='model')
path = artifact.get_path("linear_regression_model.pth")
path.download('./model/')