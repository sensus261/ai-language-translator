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
    echo -e "➿➿➿➿➿➿➿➿➿➿ \033[1;33m$1\033[0m ➿➿➿➿➿➿➿➿➿➿"
    echo -e '\n'
}

function messageNewLine {
    echo -e '\n'
}

trap cleanup INT

function cleanup {
    exit 1
}

messageTitle "Stopping project"

messageFocus "Stopping containers"
messageNewLine

docker compose stop
sleep 2

messageNewLine
messageSuccess "Containers stopped"
