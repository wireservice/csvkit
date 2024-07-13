FROM python:alpine

COPY csvkit csvkit
COPY man man
COPY README.rst setup.py .

RUN pip install --no-cache-dir .
