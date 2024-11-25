#!/bin/bash

COMPOSE_PREFIX="tf_arpspoofing"

CONTAINERS=$(docker ps --format "{{.Names}}" | grep "$COMPOSE_PREFIX-labredes")

# Check if a matching container is found
if [ -z "$CONTAINERS" ]; then
    echo "Error: No containers found with the name prefix '$COMPOSE_PREFIX-labredes'"
    read -p "Press any key to continue..."
    exit 1
fi

# Print the table header
echo -e "Nickname\tIP Address\tMAC Address\t\tDocker Hostname"

# Get the MAC address of the gateway (172.20.0.254)
GATEWAY_IP="172.20.0.254"
GATEWAY_CONTAINER=$(docker ps --format "{{.Names}}" | grep "$COMPOSE_PREFIX-gateway")
GATEWAY_MAC=$(docker exec -i "$GATEWAY_CONTAINER" arp -n "$GATEWAY_IP" | grep 'ether' | awk '{print $4}')

# Print the gateway row
echo -e "Gateway\t\t$GATEWAY_IP\t$GATEWAY_MAC\tNone"

# Create ID, Nickname mapper where ID 1=Attacker, 2=Victim 1 and 3=Victim 2
get_nickname() {
    case $1 in
        1) echo "Attacker";;
        2) echo "Victim 1";;
        3) echo "Victim 2";;
        *) echo "Unknown";;
    esac
}

for container in $CONTAINERS; do
    # Extract the IP address of the container, excluding loopback address
    IP_ADDRESS=$(docker exec -i "$container" ip a | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | grep -v '127\.0\.0\.1')
    
    # Extract the MAC address of the container
    MAC_ADDRESS=$(docker exec -i "$container" ip a | grep 'ether ' | awk '{print $2}')

    # Extract the ID from the container name
    ID=$(echo "$container" | awk -F'-' '{print $(NF-1)}' | grep -o '[0-9]*')

    # Get the nickname of the container
    NICKNAME=$(get_nickname $ID)

    # Print the table row
    echo -e "$NICKNAME\t$IP_ADDRESS\t$MAC_ADDRESS\t$container"
done

read -p "Press any key to continue..."
