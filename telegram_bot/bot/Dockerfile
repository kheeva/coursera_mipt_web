FROM python:3.6.7
MAINTAINER Oleg <oleg.ivliev1@gmail.com>
WORKDIR /workdir
COPY requirements.txt /workdir
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "/workdir/main.py" ]