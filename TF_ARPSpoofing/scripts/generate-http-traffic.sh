# Check for curl installation
if ! command -v curl &>/dev/null; then
    echo "curl is not installed. Please install curl to use this script."
    exit 1
fi

# List of HTTP-only URLs
urls=(
    "http://example.com"
    "http://httpbin.org/get"
    "http://neverssl.com"
)

# Loop through URLs and send requests
echo "Generating HTTP traffic..."
for url in "${urls[@]}"; do
    echo "Requesting: $url"
    curl -s -o /dev/null "$url"
    sleep 1  # Pause for 1 second between requests
done

echo "HTTP traffic generation complete!"

read -p "Press Enter to continue..."
