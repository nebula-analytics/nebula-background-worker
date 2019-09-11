FROM python:3.7
WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY . /app
WORKDIR /app

#RUN  ["celery", "worker", "-A schedule", "-Q nebula.express,nebula.import", "--loglevel INFO", "--name node_1"]