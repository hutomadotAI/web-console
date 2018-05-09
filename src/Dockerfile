FROM python:3.6.5-slim-jessie


# With Debian jessie slim image, need to install the mysql libs
# Don't be tempted to move to Debian stretch as that will use MariaDB
# Install translation tools, we build translations locally
RUN echo "2018-03-20" > /os_patch_date.txt

RUN apt-get update \
 && apt upgrade -y \
 && apt-get install -y \
  build-essential \
  gettext \
  libgettextpo-dev \
  libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --no-cache-dir --upgrade pip

# Gather arguments
ARG ENVIRONMENT=development
ARG CONTAINER=django
ARG SECRET_KEY

# Name container for easier discovery
LABEL container=$CONTAINER

# Use a working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.ini /usr/src/app
COPY $ENVIRONMENT.ini /usr/src/app

# Install dependencies
RUN pip install --no-cache-dir -r $ENVIRONMENT.ini

# switch to non root user
# define user IDs as ARG
ARG USERID=1000
ARG GROUPID=1000
RUN addgroup --system --gid $GROUPID appuser
RUN adduser --system --uid $USERID --gid $GROUPID appuser

# Python logs to stdout. Force stdin, stdout and stderr to be
# totally unbuffered.
ENV PYTHONUNBUFFERED 1

# Copy the code
COPY . /usr/src/app
RUN chown -R appuser:appuser /usr/src/app
USER appuser

EXPOSE 8000
