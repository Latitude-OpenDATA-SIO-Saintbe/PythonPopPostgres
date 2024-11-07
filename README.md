# PythonPopPostgres

[![Docker Compose PR Validation](https://github.com/Latitude-OpenDATA-SIO-Saintbe/PythonPopPostgres/actions/workflows/Docker.yml/badge.svg)](https://github.com/Latitude-OpenDATA-SIO-Saintbe/PythonPopPostgres/actions/workflows/Docker.yml)

## DEV environnement

1. Open the Project in GitHub Codespaces

    Go to the GitHub repository.
    Click on the "Code" button and select "Open with Codespaces".
    Wait for the Codespace to initialize. Once it's up and running, you will be inside the VS Code environment inside GitHub Codespaces.

2. Set Up the Docker Container

GitHub Codespaces comes with Docker already set up. You can start the environnement by using the provided docker-compose-dev.yml file.
Step-by-Step:

Open the Terminal inside GitHub Codespaces.

Run the following command to start the container:

```bash
docker-compose -f ./infra/docker-compose-dev.yml up -d
```

This command will run the container in detached mode. The container will be available on localhost:9595 (or Codespace's public IP if accessed externally).

To confirm the container is running, you can run:

```bash
docker-compose -f ./infra/docker-compose-dev.yml ps
```

Run Script to create and seed the database.

```bash
bash setup-py.sh
```

    Stopping Docker

When you're done working with the container, you can stop it with:

```baash
docker-compose down
```

This will stop and remove the container and also deleted all data from db.
