FROM python:3.8.6-slim-buster as deps
# Set work directory
WORKDIR /home/speedtest

# Copy files
COPY Pipfile .
COPY Pipfile.lock .

# Install pipenv
RUN pip install pipenv

FROM deps as installer
# Set work directory
WORKDIR  /home/speedtest

# Install deps
RUN pipenv install --system --deploy --ignore-pipfile

# Copy over the other pieces
COPY frameioclient frameioclient
COPY setup.py .
COPY README.md .

# Install the local frameioclient
RUN pipenv install -e . --skip-lock

# Copy over scripts and tests
COPY scripts scripts
COPY tests tests

ENV SEGMENT_WRITE_KEY=

FROM installer as runtime
ENTRYPOINT [ "pipenv", "run", "python", "scripts/benchmark/download.py" ]
