FROM python:3.10-slim

WORKDIR /app

COPY requirements_base.txt /app/requirements_base.txt
RUN pip install requirements_base.txt

CMD uvicorn main:app --reload --host localhost --port 7000