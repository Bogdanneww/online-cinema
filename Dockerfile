FROM python:3.10-slim
LABEL authors="Bohdan M."

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Копіюємо весь проект (включно з .env)
COPY . .

# 🔹 Додатково (необов'язково): створення користувача, права і т.д.
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser /app
USER appuser

# 🔹 Запуск Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
