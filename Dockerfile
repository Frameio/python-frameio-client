FROM python:slim-buster as deps

COPY Pipfile /speedtest
COPY Pipfile.lock /speedtest
RUN pip install pipenv

FROM deps as installer
RUN pipenv install

FROM installer as runtime
ENTRYPOINT [ "pipenv", "run", "./scripts/download_benchmark.py" ]