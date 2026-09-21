FROM python:3.11-slim

WORKDIR /app

COPY plane6-case/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY plane6-case/ /app/plane6-case/
COPY tests/data/ /app/tests/data/

ENV PYTHONPATH=/app
ENV DOCKER_CONTAINER=1

EXPOSE 8006 8074-8081

CMD ["python", "plane6-case/plane_runner.py"]
