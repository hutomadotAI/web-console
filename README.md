# Introduction 
Console service stores informations about users, take care of registration, login and users managements.


# Getting Started
TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:
1.	Installation process
2.	Software dependencies
3.	Latest releases
4.	API references

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
docker-compose up -d mysql redis
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

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://www.visualstudio.com/en-us/docs/git/create-a-readme). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)
