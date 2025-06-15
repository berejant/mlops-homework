# MLOps Project

This project implements a complete MLOps pipeline for training and deploying YOLO object detection models.

## Project Structure

- `mlops-hw1-dataset-and-labeling/`: Dataset preparation and labeling
- `mlops-hw2-model-training-experiments/`: Model training and experiments
- `mlops-hw3-model-inference/`: Model serving and inference
- `mlops-hw4-metrics/`: Monitoring and metrics collection

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. The pipeline consists of two main stages:

### 1. Training Stage
- Triggered on push to main branch or pull requests
- Sets up Python environment
- Installs dependencies
- Runs model training
- Executes tests
- Saves trained model as artifact

### 2. Build and Push Stage
- Downloads trained model artifacts
- Builds Docker image
- Pushes image to GitHub Container Registry (ghcr.io)

## Setup

### Prerequisites
- Python 3.9+
- Docker
- GitHub repository

### Required Permissions
The pipeline uses GitHub's built-in `GITHUB_TOKEN` for authentication. Make sure your repository has the following permissions:
- `contents: read` - To read repository contents
- `packages: write` - To push Docker images to GitHub Container Registry

## Usage

1. Push changes to the main branch or create a pull request
2. The pipeline will automatically:
   - Train the model
   - Run tests
   - Build and push Docker image to GitHub Container Registry

The Docker image will be available at: `ghcr.io/<your-github-username>/<repository-name>/yolo-model`

## Manual Trigger
You can manually trigger the pipeline from the GitHub Actions tab in your repository.

## Monitoring
The deployed model is monitored using:
- Prometheus for metrics collection
- Grafana for visualization
- Evidently for drift detection

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 