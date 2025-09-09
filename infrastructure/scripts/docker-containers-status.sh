#!/bin/bash

# List your actual service container names here (as in docker-compose.yml)
containers=(
  dockerhost
  ollama-files-translator
  ollama-api-service-files-translator
)

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GRAY='\033[1;30m'
NC='\033[0m' # No Color

# Unicode icons
ICON_RUNNING="🟢"
ICON_EXITED="🔴"
ICON_PAUSED="⏸️"
ICON_NOT_CREATED="⚪"

printf "\n%-25s %-15s %-10s\n" "CONTAINER" "STATUS" " "
printf "%-25s %-15s %-10s\n" "-------------------------" "---------------" "----------"

for name in "${containers[@]}"; do
  status=$(docker ps -a --filter "name=^/${name}$" --format "{{.Status}}")
  if [ -z "$status" ]; then
    status="not created"
    color="$GRAY"
    icon="$ICON_NOT_CREATED"
  elif [[ "$status" == Exited* ]]; then
    status="exited"
    color="$RED"
    icon="$ICON_EXITED"
  elif [[ "$status" == Up* ]]; then
    status="running"
    color="$GREEN"
    icon="$ICON_RUNNING"
  elif [[ "$status" == Paused* ]]; then
    status="paused"
    color="$YELLOW"
    icon="$ICON_PAUSED"
  fi
  printf "%-25s ${color}%-15s${NC} %-10s\n" "$name" "$status" "$icon"
done
printf "\n"