FROM python:3.7.5-alpine3.10

RUN adduser -D appuser

WORKDIR /home/appuser

RUN apk update && apk add make automake gcc g++ subversion python3-dev libressl-dev libffi-dev

RUN python -m venv venv

COPY requirements.txt ./
RUN venv/bin/pip install --no-cache-dir -r ./requirements.txt && rm requirements.txt


COPY ./token.secret /config/analytics.pickle
COPY ./ ./

RUN chown -R appuser:appuser ./

USER appuser

ENV nebula.analytics.path_to_credentials=/config/analytics.pickle

CMD python -m celery worker -B -A schedule --loglevel=debug -Q nebula.import,nebula.express -n node_1_test
