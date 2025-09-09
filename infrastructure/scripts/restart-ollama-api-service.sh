#!/bin/bash

docker compose stop ollama-api-service && sleep 2 && docker compose up -d ollama-api-service
