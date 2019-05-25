# Introduction 
Console service stores informations about users, take care of registration, login and users/bots managements.  You can familiarize yourself with the Hu:toma console by going over our [documentation](https://help.hutoma.ai/) or by checking a brief [intro video](https://www.youtube.com/watch?v=uFj73npjhbk). You can also check our [live demo](https://console.hutoma.ai/accounts/login). For further questions or issues [visit us here](https://community.hutoma.ai/).

The Bot Console is part of the Conversational AI Platform and can be also installed if you follow the instructions posted in our [main repo](https://github.com/hutomadotAI/Hutoma-Conversational-AI-Platform)

# Build and Test

### Build the Stack

This can take a while, especially the first time you run this particular command on your development system:

```bash
docker-compose build
```

### Boot the System

The first time it is run it might take a while to get started, but subsequent runs will occur quickly.

Start database and cache containers

```bash
docker-compose up -d mysql mailhog redis
```

### Running management commands

Before running the commands please check if you have a `secret.env` file. 

As with any shell command that we wish to run in our container, this is done using the `docker-compose run` command.

To migrate your application and load initial data from fixtures, run:

```bash
docker-compose run --rm django python manage.py migrate
docker-compose run --rm django python manage.py createsuperuser
```

### Start the app

For starting application in detached mode, run:

```bash
docker-compose up -d django
```

For logs checking, run:

```bash
docker-compose logs django
```

### Test

To run tests locally:

```bash
docker-compose run --rm test
```

