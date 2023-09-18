FROM --platform=linux/amd64 python:3.11-slim as build


WORKDIR /ETL_Pipeline_MySQL_BigQuery/

ENV GOOGLE_APPLICATION_CREDENTIALS=/fms/<gcp-key-file>.json
ENV PYTHONPATH="$PYTHONPATH:/usr/ETL_Pipeline_MySQL_BigQuery"

RUN curl -sSL https://sdk.cloud.google.com | bash
COPY <gcp-key-file>.json /ETL_Pipeline_MySQL_BigQuery/

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENTRYPOINT [ "python3", "src/main.py" ]