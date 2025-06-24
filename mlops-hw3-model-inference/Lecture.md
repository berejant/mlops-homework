# Інференс моделей

## Сервінг моделей використовуючи Docker

```
docker build -t fastapi-lr-model .

docker run --env-file .env -p 8080:8080 fastapi-lr-model
```

Збираємо для необхідної архітектури (наприклад, якщо збираємо на M3, а деплоїти будемо в SageMaker)
```
docker buildx create --use
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64 -t fastapi-lr-model --load .
```

http://localhost:8080/docs


Перевіряємо за допомогою наступної команди:
```
curl -X 'POST' \
  'http://localhost:8080/invocations' \
  -H 'Content-Type: application/json' \
  -d '{"years": [2024,2002]}'
```

## Сервінг моделей y Ray
https://docs.ray.io/en/latest/serve/configure-serve-deployment.html

Локальне тестування
```
serve run object_detection:entrypoint
```

Деплоємо на кластер
```
python run_serve.py
```

Перевіряємо порт форвардінг 
```
ps aux | grep "kubectl port-forward"
```

Відправляємо запит
```
python test.py
```

http://0.0.0.0:8000/docs


Видалення
```
RAY_ADDRESS='http://localhost:8265' serve shutdown
```

Різні команди роботи з serve:
```
serve build 
serve deploy
serve run
serve status
serve shutdown
```
https://docs.ray.io/en/latest/serve/api/index.html#command-line-interface-cli

## Сервінг моделей y SageMaker

Запуск локального FastAPI сервера
```
python run_local_server.py
```

Тестування з локальним URL (автоматичне визначення типу endpoint)
```
python test_model.py --url http://localhost:8000/invocations --image car.jpg --save result.jpg
```

Збірка Docker контейнера та локальне тестування
```
python build_and_test_locally.py
```

Завантаження контейнера до ECR
```
python build_and_push_to_ecr.py
```

Розгортання serverless endpoint
```
python deploy_serverless.py --custom-container
```

Тестування розгорнутого endpoint
```
python test_model.py --endpoint https://runtime.sagemaker.us-east-2.amazonaws.com/endpoints/yolov8-serverless-endpoint/invocations --image car.jpg --save my_result.jpg
```

Тестування SageMaker endpoint (за назвою endpoint)
```
python test_model.py --endpoint yolov8-serverless-endpoint --image car.jpg --save result.jpg
```

Видалення всіх створених AWS ресурсів
```
python delete_sagemaker_resources.py
```
