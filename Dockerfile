FROM python:3.10-slim

WORKDIR /app

COPY requirements_base.txt /app/requirements_base.txt
RUN pip install -r requirements_base.txt

COPY . /app
EXPOSE 7000
CMD uvicorn main:app --reload --host 0.0.0.0 --port 7000