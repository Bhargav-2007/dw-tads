FROM python:3.11-slim

WORKDIR /app

COPY plane7-presentation/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane7-presentation/ /app/plane7-presentation/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8007 8082-8088

CMD ["python", "plane7-presentation/plane_runner.py"]
