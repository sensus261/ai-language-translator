#!/bin/bash

function sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "$@"
    else
        # Linux
        sed -i "$@"
    fi
}

function messageError {
    echo -e '\n'
    echo -e "   ❌ \033[1;31m$1\033[0m"
}

function messageNewLine {
    echo -e '\n'
}

function select_menu() {
    local question="$1"
    shift
    local options=("$@")
    local selected=0

    local BOLD_WHITE='\e[1;37m'
    local ITALIC='\e[3m'
    local BOLD_YELLOW='\e[1;33m'
    local RESET='\e[0m'
    local CLEAR_LINE='\e[K'

    # Save original terminal settings
    local _STTY_ORIG_SETTINGS
    _STTY_ORIG_SETTINGS=$(stty -g)

    printf "${BOLD_WHITE}${question}${RESET} ${ITALIC}"

    printf "["
    for i in "${!options[@]}"; do
        printf " %s" "${options[$i]}"
        if ((i < ${#options[@]} - 1)); then
            printf " |"
        fi
    done
    printf " ]\n${RESET}"

    stty -echo -icanon min 1 time 0

    tput civis

    printf "\r> ${BOLD_YELLOW}%s${RESET} ${ITALIC}(↑/↓ to change, Enter to select)${RESET}${CLEAR_LINE}" "${options[$selected]}"

    while true; do
        read -rsn1 key
        case "$key" in
        $'\x03') # Handle Ctrl+C
            stty "$_STTY_ORIG_SETTINGS"
            tput cnorm
            echo
            exit 130
            ;;
        $'\x1b') # Handle arrow keys
            read -rsn2 key
            case "$key" in
            '[A') # Up arrow
                ((selected = (selected - 1 + ${#options[@]}) % ${#options[@]}))
                ;;
            '[B') # Down arrow
                ((selected = (selected + 1) % ${#options[@]}))
                ;;
            esac
            ;;
        '') # Handle Enter key
            stty "$_STTY_ORIG_SETTINGS"
            tput cnorm
            printf "\r> %s${CLEAR_LINE}\n" "${options[$selected]}"
            REPLY="${options[$selected]}"
            return $selected
            ;;
        esac
        printf "\r> ${BOLD_YELLOW}%s${RESET} ${ITALIC}(↑/↓ to change, Enter to select)${RESET}${CLEAR_LINE}" "${options[$selected]}"
    done
}

if [[ $(pwd) != *files-translator ]]; then
    messageError "You are not in the root directory. Please go to the root of the project and try again."
    exit 1
fi

messageNewLine

essential_containers=(
    "dockerhost"
    "ollama-api-service"
)

messageNewLine
messageNewLine

select_menu "Do you want to start the ollama service (ROCM variant - for AMD GPUs) aswell? If you choose not to, you have to provide an ollama service of your own and update the .env file variable related to ollama service url" "I want ollama with ROCM docker container" "I will provide my own ollama service"
choice="$REPLY"

if [[ "$choice" == "I want ollama with ROCM docker container" ]]; then
    essential_containers+=("ollama")
fi

messageNewLine
messageNewLine

echo "Starting the docker containers: '${essential_containers[@]}'"
messageNewLine


docker compose up -d "${essential_containers[@]}"

messageNewLine
