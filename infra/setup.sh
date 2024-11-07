#!/bin/bash

# Start the Docker container in detached mode
echo "Starting the Docker container..."
docker-compose -f ./infra/docker-compose-dev.yml up -d

# Confirm the container is running
echo "Checking container status..."
docker-compose -f ./infra/docker-compose-dev.yml ps

echo "All tasks completed successfully."
