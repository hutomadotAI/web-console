FROM python:3.6.6-slim-stretch


# Install translation tools, we build translations locally
RUN echo "2018-07-06" > /os_patch_date.txt

RUN apt-get update \
 && apt upgrade -y \
 && apt-get install -y \
  build-essential \
  gettext \
  libgettextpo-dev \
  && rm -rf /var/lib/apt/lists/*

# Use MySQL's PGP signature from https://dev.mysql.com/doc/refman/5.7/en/checking-gpg-signature.html
COPY mysql-gpg-sig /tmp
# Install MySql libraries from MySQL apt repo
RUN apt-key add /tmp/mysql-gpg-sig \
 && echo "deb http://repo.mysql.com/apt/debian stretch mysql-5.7" | tee /etc/apt/sources.list.d/mysql.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
  libmysqlclient-dev

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
RUN mkdir /kb && chown appuser:appuser /kb

USER appuser

EXPOSE 8000
