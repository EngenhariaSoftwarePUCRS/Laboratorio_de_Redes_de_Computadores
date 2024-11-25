#!/bin/bash

# Check if a numeric suffix is provided
if [ -z "$1" ]; then
    echo "Usage: ./docker-exec.sh <suffix>"
    echo "Make sure to provide a numeric suffix to identify the container."
    read -p "Press any key to continue..."
    exit 1
fi

# Extract the suffix argument
SUFFIX=$1

# Find the container name matching the suffix
CONTAINER=$(docker ps --format "{{.Names}}" | grep "tf_sockraw-labredes${SUFFIX}")

# Check if a matching container is found
if [ -z "$CONTAINER" ]; then
    echo "Error: No container found with suffix '${SUFFIX}'."
    exit 1
fi

# Execute an interactive shell in the matched container
echo "Connecting to container: $CONTAINER"
docker exec -it "$CONTAINER" bash
