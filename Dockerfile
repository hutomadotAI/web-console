FROM python:3.6

# Gather arguments
ARG ENVIRONMENT=development
ARG CONTAINER=django
ARG SECRET_KEY

# Name container for easier discovery
LABEL container=$CONTAINER

# Python logs to stdout. Force stdin, stdout and stderr to be
# totally unbuffered.
ENV PYTHONUNBUFFERED 1

# Use a working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install translation tools, we build translations locally
RUN apt-get update && apt-get install -y \
  gettext \
  libgettextpo-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.ini /usr/src/app
COPY $ENVIRONMENT.ini /usr/src/app

# Install dependencies
RUN pip install -r $ENVIRONMENT.ini

# Copy the code
COPY . /usr/src/app



