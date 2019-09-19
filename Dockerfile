FROM python:latest
WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY ./token.secret /config/analytics.pickle
ENV nebula.analytics.path_to_credentials="/creds/analytics.pickle"

COPY . /app
WORKDIR /app

CMD python -m celery worker -B -A schedule --loglevel=debug -Q nebula.import,nebula.express -n node_1_test