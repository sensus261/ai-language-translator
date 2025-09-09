#!/bin/bash

echo -e '\n'
echo -e '\n'
echo -e "➿➿➿➿➿➿➿➿➿➿ \033[1;33m Starting OLLAMA API service container shell \033[0m ➿➿➿➿➿➿➿➿➿➿"
echo -e '\n'

# Prompt the user to choose between normal user or root using fzf
choice=$(echo -e "Normal User\nRoot" | fzf --height 10% --prompt="Select user to start shell: ")

# Execute the corresponding docker compose command based on the user's choice
if [ "$choice" == "Normal User" ]; then
    docker compose exec -u 1000:1000 ollama-api-service /bin/bash
elif [ "$choice" == "Root" ]; then
    docker compose exec ollama-api-service /bin/bash
else
    echo "Invalid choice. Exiting."
    exit 1
fi
