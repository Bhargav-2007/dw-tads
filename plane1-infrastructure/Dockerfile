FROM python:3.11-slim

WORKDIR /app

COPY plane1-infrastructure/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane1-infrastructure/ /app/plane1-infrastructure/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8001 8011-8022

CMD ["python", "plane1-infrastructure/plane_runner.py"]
