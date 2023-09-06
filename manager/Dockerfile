FROM python:3.11

RUN mkdir /manager_app

WORKDIR /manager_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
