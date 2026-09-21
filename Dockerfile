FROM python:3.11.11-slim-bookworm
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY demo /app/demo
COPY intel /app/intel
COPY licenses /app/licenses
COPY tests /app/tests
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN useradd --uid 10001 --create-home demo
USER demo
CMD ["uvicorn", "demo.app:app", "--host", "0.0.0.0", "--port", "8000"]
