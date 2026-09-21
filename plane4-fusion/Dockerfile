FROM python:3.11-slim

WORKDIR /app

COPY plane4-fusion/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane4-fusion/ /app/plane4-fusion/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8004 8055-8064

CMD ["python", "plane4-fusion/plane_runner.py"]
