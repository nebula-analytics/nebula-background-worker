FROM python:latest
WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

VOLUME "/creds"
COPY ./token.secret /creds/analytics.pickle

COPY . /app
WORKDIR /app