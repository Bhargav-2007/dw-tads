FROM python:3.11-slim

WORKDIR /app

COPY plane3-analytics/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane3-analytics/ /app/plane3-analytics/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8003 8037-8054

CMD ["python", "plane3-analytics/plane_runner.py"]
