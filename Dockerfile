FROM python:alpine

COPY csvkit setup.py .

RUN pip install --no-cache-dir .
