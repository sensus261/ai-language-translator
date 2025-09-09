#!/bin/bash

docker compose stop ollama && sleep 2 && docker compose up -d ollama
