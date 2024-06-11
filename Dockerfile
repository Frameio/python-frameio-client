FROM python:3.11-buster as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /frameio

COPY README.md README.md
COPY pyproject.toml poetry.lock ./
COPY frameioclient frameioclient

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev

ENTRYPOINT [ "poetry", "run", "fiocli" ]
