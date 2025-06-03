# Використовуємо базовий образ Bitnami PyTorch
FROM bitnami/pytorch:2.3.1

# Створюємо директорію для кешу WANDB
RUN mkdir -p /app/.cache/wandb
ENV WANDB_CACHE_DIR=/app/.cache/wandb

# Створюємо директорію для моделі
RUN mkdir -p /app/model

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копіюємо необхідні файли
COPY download_model.py download_model.py
COPY main.py main.py
COPY start.sh start.sh


# Додатково видаляємо стандартний entrypoint Bitnami, якщо це необхідно
RUN rm /opt/bitnami/scripts/pytorch/entrypoint.sh

# Встановлюємо entrypoint на start.sh
ENTRYPOINT ["./start.sh"]
