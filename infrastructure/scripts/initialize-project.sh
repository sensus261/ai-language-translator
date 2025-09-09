#!/bin/bash

function messageSuccess {
    echo -e '\n'
    echo -e "   🚀 \033[1;32m$1\033[0m"
}

function messageError {
    echo -e '\n'
    echo -e "   ❌ \033[1;31m$1\033[0m"
}

function messageWarning {
    echo -e "   🔼 \033[1;33m$1\033[0m"
}

function messageFocus {
    echo -e "   📖 \033[1;34m$1\033[0m"
}

function messageTitle {
    echo -e '\n'
    echo -e '\n'
    echo -e '\n'
    echo -e '\n'
    echo -e "➿➿➿➿➿➿➿➿➿➿ \033[1;33m$1\033[0m ➿➿➿➿➿➿➿➿➿➿"
    echo -e '\n'
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

trap cleanup INT

function cleanup {
    # Add any cleanup commands you need here
    messageNewLine
    messageWarning "Script interrupted. Cleaning up..."
    messageNewLine

    # Terminate background processes explicitly
    docker compose stop
    exit 1
}

function execContainerCommand {
    container=$1
    command=$2
    ignoreOutput=$3

    if [[ "$ignoreOutput" == "true" ]]; then
        docker compose exec $user_flag $container /bin/bash -c "XDEBUG_MODE=off $command > /dev/null 2>&1"
        return
    fi

    docker compose exec $user_flag $container /bin/bash -c "XDEBUG_MODE=off $command"
}

##########################################################################
############## Check if user is in project root directory ################
##########################################################################

if [[ $(pwd) != *files-translator ]]; then
    messageError "You are not in the root directory. Please go to the root of the project and try again."
    exit 1
fi

###############################################
############## Clear terminal? ################
###############################################

messageNewLine
select_menu "Do you want to clear the terminal (improves visibility on what's going in here)?" "YES" "NO"
choice="$REPLY"

if [[ "$choice" == "YES" ]]; then
    clear
    messageSuccess "Terminal cleared. Starting to init / reset the project..."
fi

###########################################
############## Clear logs? ################
###########################################

messageNewLine
select_menu "Do you want to clear the service logs?" "YES" "NO"
choice="$REPLY"

if [[ "$choice" == "YES" ]]; then
    ./infrastructure/scripts/clear-logs.sh
fi

##########################################################
############## Stopping docker containers ################
##########################################################

messageTitle "Stopping docker containers..."
docker compose stop
messageSuccess "Docker containers stopped."

##################################################
############## Data wipe confirm? ################
##################################################

messageNewLine
select_menu "This script will begin to initialize / reset the project. If the project was already installed before, all the data from database will be wiped out. Confirm?" "YES" "NO"
choice="$REPLY"

if [[ "$choice" == "NO" ]]; then
    messageError "Reset project aborted."
    exit 1
fi

sleep 1

##################################################################
############## Reset previous project instalation ################
##################################################################

messageTitle "Removing docker containers..."
docker compose down -v
messageSuccess "Docker containers removed."

sleep 1


#############################################################
############## Start fresh docker containers ################
#############################################################

messageTitle "Starting fresh docker containers..."
./infrastructure/scripts/start-project.sh

messageSuccess "Docker containers are up and running."

sleep 1

#######################################
############## SUCCESS ################
#######################################

messageNewLine
messageNewLine
messageNewLine
messageNewLine

messageSuccess "Project initialized successfully. You can start using the platform now."

messageNewLine
messageNewLine
messageNewLine
messageNewLine

messageWarning "Services URLs:"
messageNewLine
messageFocus "TRANSLATOR MENU:                   http://localhost:5001/"
messageNewLine
messageNewLine

messageNewLine
messageNewLine
