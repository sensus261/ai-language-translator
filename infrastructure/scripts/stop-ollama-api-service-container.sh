#!/bin/bash

echo -e '\n'
echo -e '\n'
echo -e "➿➿➿➿➿➿➿➿➿➿ \033[1;33m Stopping OLLAMA API service container \033[0m ➿➿➿➿➿➿➿➿➿➿"
echo -e '\n'

docker compose stop ollama-api-service
