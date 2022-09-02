FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /scladdv
WORKDIR /scladdv
COPY requirements.txt /scladdv/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /scladdv/
