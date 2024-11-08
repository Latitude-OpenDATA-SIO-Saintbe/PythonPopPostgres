#!/bin/bash

# Start the Docker container in detached mode
echo "Starting the Docker container..."
docker-compose -f ./infra/docker-compose-test.yml up -d

# Confirm the container is running
echo "Checking container status..."
docker-compose -f ./infra/docker-compose-test.yml ps

bash setup-py.sh

echo "All tasks completed successfully."
