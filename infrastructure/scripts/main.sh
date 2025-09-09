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

execute_script() {
    local script_path="$1"
    local script_name=$(basename "$script_path")

    messageTitle "Executing: $script_name"

    # Check if script exists and is executable
    if [[ ! -f "$script_path" ]]; then
        messageError "Script not found: $script_path"
        return 1
    fi

    if [[ ! -x "$script_path" ]]; then
        messageWarning "Script is not executable. Making it executable..."
        chmod +x "$script_path"
    fi

    # Execute the script
    echo -e "🔄 Running script: $script_name"
    echo -e "📁 Path: $script_path"
    echo -e "⏱️  Started at: $(date)"
    echo -e "\n"

    # Run the script and capture exit code
    bash "$script_path"
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        messageSuccess "Script completed successfully! ✅"
    else
        messageError "Script failed with exit code: $exit_code ❌"
    fi

    echo -e "\n"
    echo -e "⏱️  Finished at: $(date)"
    echo -e "\n"

    return $exit_code
}

# Function to check if fzf is available
check_fzf() {
    if ! command -v fzf &>/dev/null; then
        messageWarning "fzf is not installed. Using fallback menu system."
        return 1
    fi
    return 0
}

# Function to show header
show_header() {
    clear
    echo -e "\n"
    echo -e "┌─────────────────────────────────────────────────────────────────────────────────┐"
    echo -e "│                        🚀 Files translator ---- Scripts                         │"
    echo -e "├─────────────────────────────────────────────────────────────────────────────────┤"
    echo -e "│  Manage your files translation project with ease using these automated scripts  │"
    echo -e "│                                                                                 │"
    echo -e "│  📋 Categories:                                                                 │"
    echo -e "│    • Project Management - Start/stop/restart entire project                     │"
    echo -e "│    • Service Management - Individual service controls                           │"
    echo -e "│    • Utilities - Backup, logs, and maintenance tools                            │"
    echo -e "└─────────────────────────────────────────────────────────────────────────────────┘"
    echo -e "\n"
}

# Function to get script descriptions
get_script_description() {
    case "$1" in
    "initialize-project.sh") echo "🏗️  Initialize project environment" ;;
    "start-project.sh") echo "▶️  Start all project services" ;;
    "restart-project.sh") echo "🔄 Restart all project services" ;;
    "stop-project.sh") echo "⏹️  Stop all project services" ;;
    "clear-logs.sh") echo "🧹 Clear all service logs" ;;
    "start-ollama-api-service-container-shell.sh") echo "🖥️  Access Ollama API container shell" ;;
    "restart-ollama-api-service.sh") echo "🔄 Restart Ollama API service" ;;
    "stop-ollama-api-service-container.sh") echo "⏹️  Stop Ollama API service container" ;;
    "start-ollama-service-container-shell.sh") echo "🖥️  Access Ollama service container shell" ;;
    "restart-ollama-service.sh") echo "🔄 Restart Ollama service" ;;
    "stop-ollama-service-provider-container.sh") echo "⏹️  Stop Ollama service provider container" ;;
    "docker-containers-status.sh") echo "📄 List status of all Docker containers" ;;
    *) echo "📄 Script execution" ;;
    esac
}

# Fallback menu system (without fzf)
create_fallback_menu() {
    local scripts=("$@")
    local menu_items=()

    echo -e "\n┌─────────────────────────────────────────────────────────────────────────────────┐"
    echo -e "│                             Available Scripts                                   │"
    echo -e "├─────────────────────────────────────────────────────────────────────────────────┤"

    for i in "${!scripts[@]}"; do
        local script_name=$(basename "${scripts[$i]}")
        local description=$(get_script_description "$script_name")
        local clean_name=$(echo "$script_name" | sed 's/\.sh$//' | sed 's/-/ /g')
        echo -e "│  $((i + 1)). $clean_name"
        echo -e "│     $description"
        echo -e "├─────────────────────────────────────────────────────────────────────────────────┤"
    done

    echo -e "│  0. 🔙 Back to categories                                                       │"
    echo -e "└─────────────────────────────────────────────────────────────────────────────────┘"

    echo -e "\n"
    read -p "Enter your choice (0-${#scripts[@]}): " choice

    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 0 ] && [ "$choice" -le "${#scripts[@]}" ]; then
        if [ "$choice" -eq 0 ]; then
            return 1 # Back to categories
        else
            local selected_script_path="${scripts[$((choice - 1))]}"
            echo "$(basename "$selected_script_path")"
            return 0
        fi
    else
        messageError "Invalid choice. Please try again."
        return 2 # Invalid choice
    fi
}

# Function to create script menu with descriptions
create_script_menu() {
    local scripts=("$@")
    local menu_items=()

    if check_fzf; then
        for script in "${scripts[@]}"; do
            local script_name=$(basename "$script")
            local description=$(get_script_description "$script_name")
            local clean_name=$(echo "$script_name" | sed 's/\.sh$//' | sed 's/-/ /g')
            menu_items+=("$clean_name → $description")
        done

        local selected_item=$(printf "%s\n" "${menu_items[@]}" | fzf --height 60% --border --prompt="🔍 Select script: " --preview='echo "📝 {}" | fold -w 50' --header="Use ↑↓ to navigate, Enter to select, Esc to cancel")

        if [[ -n "$selected_item" ]]; then
            local clean_name=$(echo "$selected_item" | cut -d'→' -f1 | sed 's/[[:space:]]*$//')
            # Convert back to original filename
            local original_name=$(echo "$clean_name" | sed 's/ /-/g').sh
            echo "$original_name"
            return 0
        else
            return 1 # User cancelled (Esc)
        fi
    else
        # Use fallback menu
        create_fallback_menu "${scripts[@]}"
    fi
}

# Enhanced execution with progress
create_script_menu() {
    local scripts=("$@")
    local menu_items=()

    if check_fzf; then
        for script in "${scripts[@]}"; do
            local script_name=$(basename "$script")
            local description=$(get_script_description "$script_name")
            menu_items+=("$description")
        done

        local selected_item=$(printf "%s\n" "${menu_items[@]}" | fzf --height 60% --border --prompt="🔍 Select script: " --preview='echo "📝 {}" | fold -w 50' --header="Use ↑↓ to navigate, Enter to select, Esc to cancel")

        if [[ -n "$selected_item" ]]; then
            # Find the original script by matching the description
            for script in "${scripts[@]}"; do
                local script_name=$(basename "$script")
                local description=$(get_script_description "$script_name")
                if [[ "$description" == "$selected_item" ]]; then
                    echo "$script_name"
                    return 0
                fi
            done
        else
            return 1 # User cancelled (Esc)
        fi
    else
        # Use fallback menu
        create_fallback_menu "${scripts[@]}"
    fi
}

# Fallback category menu
show_fallback_categories() {
    echo -e "\n┌─────────────────────────────────────────────────────────────────────────────────┐"
    echo -e "│                               Categories                                        │"
    echo -e "├─────────────────────────────────────────────────────────────────────────────────┤"
    echo -e "│  1. 🚀 Project Management                                                       │"
    echo -e "│  2. 🤖 Ollama API Service                                                       │"
    echo -e "│  3. ⚙️  Ollama Provider                                                          │"
    echo -e "│  4. 📋 Other Scripts                                                            │"
    echo -e "│  0. 🚪 Exit                                                                      │"
    echo -e "└─────────────────────────────────────────────────────────────────────────────────┘"

    echo -e "\n"
    read -p "Enter your choice (0-5): " choice

    case "$choice" in
    1) echo "🚀 Project Management" ;;
    3) echo "🤖 Ollama API Service" ;;
    4) echo "⚙️  Ollama Provider" ;;
    5) echo "📋 Other Scripts" ;;
    0) echo "EXIT" ;;
    *) echo "INVALID" ;;
    esac
}

# Main execution starts here
show_header

if [[ $(pwd) != *files-translator ]]; then
    messageError "You are not in the root directory. Please go to the root of the project and try again."
    exit 1
fi

# Directory containing the scripts
SCRIPT_DIR="./infrastructure/scripts"

# Arrays for script groups
general_project_scripts=()
main_api_service_scripts=()
ollama_api_service_scripts=()
ollama_service_scripts=()
other_scripts=()

# Categorize scripts
for script in $SCRIPT_DIR/*.sh; do
    script_name=$(basename "$script")
    # Exclude the current script (main.sh)
    if [ "$script_name" == "main.sh" ]; then
        continue
    fi

    case "$script_name" in
    initialize-project.sh | start-project.sh | restart-project.sh | stop-project.sh | clear-logs.sh | docker-containers-status.sh | update-to-last-version.sh | start-only-ai-part.sh)
        general_project_scripts+=("$script")
        ;;
    start-ollama-api-service-container-shell.sh | restart-ollama-api-service.sh | stop-ollama-api-service-container.sh)
        ollama_api_service_scripts+=("$script")
        ;;
    start-ollama-service-container-shell.sh | restart-ollama-service.sh | stop-ollama-service-provider-container.sh)
        ollama_service_scripts+=("$script")
        ;;
    *)
        other_scripts+=("$script")
        ;;
    esac
done

# Main loop to handle category selection and navigation
while true; do
    # Try to use fzf for categories, fallback to numbered menu
    if check_fzf; then
        categories=("🚀 Project Management" "🤖 Ollama API Service" "⚙️  Ollama Provider" "📋 Other Scripts")
        selected_category=$(printf "%s\n" "${categories[@]}" | fzf --height 15% --border --prompt="🎯 Select category: " --header="Files Translator - Script Categories")
    else
        selected_category=$(show_fallback_categories)
    fi

    if [[ -z "$selected_category" || "$selected_category" == "EXIT" ]]; then
        messageSuccess "Goodbye! 👋"
        exit 0
    fi

    if [[ "$selected_category" == "INVALID" ]]; then
        messageError "Invalid choice. Please try again."
        continue
    fi

    case "$selected_category" in
    "🚀 Project Management")
        if [ ${#general_project_scripts[@]} -gt 0 ]; then
            selected_script=$(create_script_menu "${general_project_scripts[@]}")
            script_selection_result=$?
            script_array=("${general_project_scripts[@]}")
        else
            messageWarning "No scripts found in this category."
            continue
        fi
        ;;
    "🤖 Ollama API Service")
        if [ ${#ollama_api_service_scripts[@]} -gt 0 ]; then
            selected_script=$(create_script_menu "${ollama_api_service_scripts[@]}")
            script_selection_result=$?
            script_array=("${ollama_api_service_scripts[@]}")
        else
            messageWarning "No scripts found in this category."
            continue
        fi
        ;;
    "⚙️  Ollama Provider")
        if [ ${#ollama_service_scripts[@]} -gt 0 ]; then
            selected_script=$(create_script_menu "${ollama_service_scripts[@]}")
            script_selection_result=$?
            script_array=("${ollama_service_scripts[@]}")
        else
            messageWarning "No scripts found in this category."
            continue
        fi
        ;;
    "📋 Other Scripts")
        if [ ${#other_scripts[@]} -gt 0 ]; then
            selected_script=$(create_script_menu "${other_scripts[@]}")
            script_selection_result=$?
            script_array=("${other_scripts[@]}")
        else
            messageWarning "No scripts found in this category."
            continue
        fi
        ;;
    *)
        messageError "Invalid category selected."
        continue
        ;;
    esac

    # Handle the script selection result
    if [[ $script_selection_result -eq 1 ]]; then
        # User chose to go back to categories (return code 1)
        continue
    elif [[ $script_selection_result -eq 2 ]]; then
        # Invalid choice, retry the same category (return code 2)
        continue
    fi

    # Execute the selected script
    if [[ -n "$selected_script" ]]; then
        # Find the full path for the selected script
        full_script_path=""
        for script in "${script_array[@]}"; do
            if [[ "$(basename "$script")" == "$selected_script" ]]; then
                full_script_path="$script"
                break
            fi
        done

        if [[ -n "$full_script_path" ]]; then
            execute_script "$full_script_path"
        else
            messageError "Script not found: $selected_script"
        fi
    else
        messageWarning "No script selected."
    fi

    # If we reach here, user chose option 2 (run another script from same category)
    # The loop will continue
done
