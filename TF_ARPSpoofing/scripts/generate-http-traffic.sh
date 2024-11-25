# Check for curl installation
if ! command -v curl &>/dev/null; then
    echo "curl is not installed. Please install curl to use this script."
    exit 1
fi

# List of HTTP-only URLs
urls=(
    "http://example.com"
    "http://www.pucrs.br/facin/agenda/"
    "http://globoesporte.globo.com/blogs/especial-blog/brasil-mundial-fc/post/jogo-da-paz-maradona-se-estranha-com-veron-e-deixa-o-gramado-irritado.html"
    "http://www.gshow.globo.com/tv/noticia/2016/10/angelica-e-luciano-huck-sao-entrevistados-no-programa-do-jo.html"
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
