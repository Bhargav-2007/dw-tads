FROM python:3.11-slim

WORKDIR /app

COPY plane5-legal/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane5-legal/ /app/plane5-legal/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8005 8065-8073

CMD ["python", "plane5-legal/plane_runner.py"]
