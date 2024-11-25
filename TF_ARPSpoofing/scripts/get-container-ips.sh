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

# Print the table header
echo -e "ID\tAddress\t\tDocker Hostname"

for container in $CONTAINER; do
    # Extract the IP address of the container, excluding loopback address
    IP_ADDRESS=$(docker exec -i "$container" ip a | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | grep -v '127\.0\.0\.1')
    # Extract the ID from the container name
    ID=$(echo "$container" | awk -F'-' '{print $(NF-1)}' | grep -o '[0-9]*')
    # Print the table row
    echo -e "$ID\t$IP_ADDRESS\t$container"
done

read -p "Press any key to continue..."
