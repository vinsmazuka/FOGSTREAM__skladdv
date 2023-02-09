FROM python:3.8
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install nano
ENV PYTHONUNBUFFERED 1
RUN mkdir /scladdv
WORKDIR /scladdv
COPY requirements.txt /scladdv/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /scladdv/
