#!/bin/bash

function messageError {
    echo -e '\n'
    echo -e "   ❌ \033[1;31m$1\033[0m"
}

function messageSuccess {
    echo -e '\n'
    echo -e "   🚀 \033[1;32m$1\033[0m"
}

if [[ $(pwd) != *files-translator ]]; then
    messageError "You are not in the root directory. Please go to the root of the project and try again."
    exit 1
fi

cd services/files-translator-service/original_fallout_files && rm Fallout4_en_fr.xml && cp __Fallout4_en_fr.xml Fallout4_en_fr.xml && rm -rf ./Fallout4_en_ro.xml

cd ../../..

messageSuccess "Fallout files reloaded from original_fallout_files directory."