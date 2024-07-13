FROM python:alpine

COPY csvkit README.rst setup.py .

RUN pip install --no-cache-dir .
