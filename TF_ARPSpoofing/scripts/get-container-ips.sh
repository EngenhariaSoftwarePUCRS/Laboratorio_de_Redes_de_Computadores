#!/bin/bash

# Extract the suffix argument
SUFFIX=$1

# Find the container name matching the suffix
CONTAINER=$(docker ps --format "{{.Names}}" | grep "tf_arpspoofing-labredes")

# Check if a matching container is found
if [ -z "$CONTAINER" ]; then
    echo "Error: No container found with suffix '${SUFFIX}'."
    read -p "Press any key to continue..."
    exit 1
fi

for container in $CONTAINER; do
    echo "Container: $container"
    # Extract the IP address of the container and display it
    docker exec -i "$container" ip a | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
done

read -p "Press any key to continue..."
