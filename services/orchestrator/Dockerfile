FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY burner_orchestrator ./burner_orchestrator
COPY main.py .
ENV PYTHONPATH=/app:/app/identity_pkg:/app/buy_assist_pkg
EXPOSE 8090
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
