FROM python:alpine

COPY csvkit man README.rst setup.py .

RUN pip install --no-cache-dir .
