FROM python:3.9.5-slim-buster

MAINTAINER  TechniCollins "technicollins.business@gmail.com"

ENV HOME /root
ENV APP_HOME /application/
ENV C_FORCE_ROOT=true
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential

RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# upgrade pip
RUN pip3 install --upgrade pip

# Install pip packages
ADD ./requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

# Copy code into Image
ADD ./servicenow_twitter_web/ $APP_HOME
