FROM python:3.9

MAINTAINER "hurjn96@gmail.com"

RUN apt-get update
RUN apt-get install -y locales
RUN locale-gen "en_US.UTF-8"
RUN dpkg-reconfigure locales

WORKDIR /app

RUN mkdir /app/volume
COPY museum/ ./museum
COPY web/ ./web
COPY setup.py ./setup.py

RUN pip install -e .

WORKDIR ./web
RUN python3 manage.py migrate

EXPOSE 8000

ENTRYPOINT [ "python3", "manage.py", "runserver", "0.0.0.0:8000"]
