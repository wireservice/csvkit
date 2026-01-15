FROM python:alpine

COPY csvkit csvkit
COPY man man
COPY README.rst pyproject.toml .

RUN pip install --no-cache-dir .
