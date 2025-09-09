#!/bin/bash

# Function to print a message using unicode characters
last_chain_index=0

# Function to print a message in a nice way using unicode characters
print_message() {
    message=$1
    unicode=$2

    len=${#message}
    num_chars=$(($len - 4))

    if [ $last_chain_index -ne 0 ]; then
        half_num_chars=$(($last_chain_index))
    else
        half_num_chars=$(($len / 2))
    fi

    last_chain_index=$(($len / 2))

    top_border=$(printf '═%.0s' $(seq 1 $num_chars))
    bottom_border=$(printf '═%.0s' $(seq 1 $num_chars))
    top_chains_space=$(printf ' %.0s' $(seq 1 $half_num_chars))
    bottom_chains_space=$(printf ' %.0s' $(seq 1 $last_chain_index))

    echo "$top_chains_space⛓$top_chains_space"
    echo "$top_chains_space⛓$top_chains_space"
    echo "╔═.$unicode.$top_border.═╗"
    echo "   $message"
    echo "╚═.$bottom_border.$unicode.═╝"
    echo "$bottom_chains_space⛓$bottom_chains_space"
    echo "$bottom_chains_space⛓$bottom_chains_space"

    sleep 1
}

# Function to handle errors
handle_error() {
    app=$1
    step=$2

    print_message "❌ [PRE-COMMIT] Error while executing step '$step' for application '$app'." "✘"
    exit 1
}

# Function to chech the health status of containers
check_containers_health_status() {
    containers=(
        "main-api-service"
        "dockerhost"
        "redis"
    )

    print_message "⌛ [PRE-COMMIT] Checking the health status of containers... " "🔍"

    for container in "${containers[@]}"; do
        # status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null)
        status=$(docker ps --filter "name=$container" --format '{{.Status}}' | cut -d ' ' -f 1)
        if ! [[ "$status" =~ "Up" ]]; then
            print_message "❌ [PRE-COMMIT] Container '$container' is not running." "✘"
            print_message "❌ [PRE-COMMIT] Container '$container' has status '$status'." "✘"
            exit 1
        fi
    done

    print_message "✅ [PRE-COMMIT] All containers are running." "✔"
}

# Function to modify the .env files
modify_env_file() {
    app=$1
    from=$2
    to=$3
    env=$4

    docker compose exec -T $app /bin/sh -c "sed -i 's/$from/$to/g' $env"
}

# Function to run lint
run_lint() {
    app=$1

    print_message "⌛ [PRE-COMMIT] Running the linter for [$app]... " "🔍"

    docker compose exec -T $app yarn lint
    if [ $? -ne 0 ]; then
        handle_error $app "Linting and fixing the app"
    fi
}

run_build() {
    app=$1

    print_message "⌛ [PRE-COMMIT] Building [$app]... " "🔍"

    docker compose exec -T $app yarn build
    if [ $? -ne 0 ]; then
        handle_error $app "Building the app"
    fi
}

execContainerCommand() {
    container=$1
    command=$2
    ignoreOutput=$3

    print_message "⌛ [PRE-COMMIT] Executing [$command] in [$container]... " "🔍"

    if [[ "$ignoreOutput" == "true" ]]; then
        docker compose exec -T $container /bin/bash -c "XDEBUG_MODE=off $command > /dev/null 2>&1"
        return
    fi

    docker compose exec -T $container /bin/bash -c "XDEBUG_MODE=off $command"
}

# Function to run build
run_build() {
    app=$1

    print_message "⌛ [PRE-COMMIT] Building [$app]... " "🔍"

    docker compose exec -T $app yarn build
    if [ $? -ne 0 ]; then
        handle_error $app "Building the app"
    fi
}

run_duster() {
    app=$1

    print_message "⌛ [PRE-COMMIT] Running duster for [$app]... " "🔍"

    docker compose exec -T $app ./vendor/bin/duster fix
    if [ $? -ne 0 ]; then
        handle_error $app "Running duster"
    fi
}

handle_api_hooks() {

    print_message "⌛ [PRE-COMMIT] [MAIN-API-SERVICE] Regenerating IDE helper files... ⌛"

    api_dir=services/main-api-service

    api_file_changed=$(git diff --cached --name-only | grep "^$api_dir/")

    if [ -z "$api_file_changed" ]; then
        print_message "✅ [PRE-COMMIT] [MAIN-API-SERVICE] No changes detected. No need to regenerate IDE helper files." "✔"
        return 0
    fi

    execContainerCommand "main-api-service" "php artisan ide-helper:generate"
    git add $api_dir/_ide_helper.php

    execContainerCommand "main-api-service" "php artisan ide-helper:models --nowrite"
    git add $api_dir/_ide_helper_models.php

    print_message "🚀 [PRE-COMMIT] [MAIN-API-SERVICE] Finished regenerating IDE helper files. 🚀"
}

handle_linting_on_api() {
    print_message "⌛ [PRE-COMMIT] [MAIN-API-SERVICE] Linting... ⌛"

    api_dir=services/main-api-service

    api_file_changed=$(git diff --cached --name-only --diff-filter=ACM | grep "^$api_dir/")

    if [ -z "$api_file_changed" ]; then
        print_message "✅ [PRE-COMMIT] [MAIN-API-SERVICE] No changes detected. No need to lint files." "✔"
        return 0
    fi

    run_duster "main-api-service"

    for file in $api_file_changed; do
        git add $file
    done

    print_message "✅ [PRE-COMMIT] [MAIN-API-SERVICE] The linter were executed successfully!" "✨"
}

# To suppress the annoying warns which we don't care about
export DB_DATABASE="database_name"
export XDEBUG_HOST="xdebug_host_name"

# Check docker containers health status
check_containers_health_status

# [MAIN-API-SERVICE] Run the hooks
handle_api_hooks
if [ $? -eq 0 ]; then
    handle_linting_on_api
fi

# FINISH LINE
print_message "✨ [PRE-COMMIT] Finished! Your commit has been made!" "✨"
