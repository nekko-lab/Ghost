FROM python:3

WORKDIR /ghost

COPY config.py ./
COPY data.py ./
COPY main.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt