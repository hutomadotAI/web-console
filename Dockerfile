FROM python:3.6

# Gather arguments
ARG ENVIRONMENT=development
ARG CONTAINER=django
ARG SECRET_KEY

# Name container for easier discovery
LABEL container=$CONTAINER

# Install translation tools, we build translations locally
RUN apt-get update && apt-get install -y \
  gettext \
  libgettextpo-dev \
  && rm -rf /var/lib/apt/lists/*

# Use a working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.ini /usr/src/app
COPY $ENVIRONMENT.ini /usr/src/app

# Install dependencies
RUN pip install -r $ENVIRONMENT.ini

# switch to non root user
# define user IDs as ARG
ARG USERID=1000
ARG GROUPID=1000
RUN addgroup --gid=$GROUPID appuser
RUN adduser --uid=$USERID --gid=$GROUPID appuser

# Python logs to stdout. Force stdin, stdout and stderr to be
# totally unbuffered.
ENV PYTHONUNBUFFERED 1

# Copy the code
COPY . /usr/src/app
RUN chown -R appuser:appuser /usr/src/app
USER appuser



