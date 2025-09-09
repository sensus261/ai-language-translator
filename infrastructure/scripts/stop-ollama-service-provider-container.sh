#!/bin/bash

echo -e '\n'
echo -e '\n'
echo -e "➿➿➿➿➿➿➿➿➿➿ \033[1;33m Stopping OLLAMA service provider container \033[0m ➿➿➿➿➿➿➿➿➿➿"
echo -e '\n'

docker compose stop ollama
