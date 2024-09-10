FROM python:3.11.5-slim-bookworm


RUN apt-get update -y && apt-get install --no-install-recommends -y \
    gcc \
    libpq-dev \
    python3-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    default-jre


ENV VIRTUAL_ENV=/opt/venv
ENV APP_HOME=/opt/app
WORKDIR ${APP_HOME}

RUN groupadd -r appgrp && useradd -r -g appgrp appuser && \
    mkdir -p /opt/run/celery && chown -R appuser:appgrp /opt/run

ADD requirements.txt .

RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install black~=22.3.0

