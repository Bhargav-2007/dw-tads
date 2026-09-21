FROM python:3.11-slim

WORKDIR /app

COPY plane2-collection/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane2-collection/ /app/plane2-collection/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8002 8023-8036

CMD ["python", "plane2-collection/plane_runner.py"]
