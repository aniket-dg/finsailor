FROM python:3.11.5-slim-bookworm
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /code/
WORKDIR /code
RUN pip3.11 install --upgrade pip \
    && pip3.11 install -r requirements.txt
