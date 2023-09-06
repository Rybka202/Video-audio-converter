FROM python:3.11

RUN mkdir /executor_app

WORKDIR /executor_app

COPY requirements.txt .

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh