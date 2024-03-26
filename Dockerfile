FROM python:3.11

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt
RUN apt update && apt install jq make -y

copy . /app
