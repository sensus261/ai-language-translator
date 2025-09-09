#!/bin/bash

# Check if the pre-commit file exists in the .git/hooks directory
if [ -f .git/hooks/pre-commit ]; then
    echo "Pre-commit hook already exists. Deleting old hook..."
    rm .git/hooks/pre-commit
fi

# Copy the pre-commit file from the infrastructure/git/hooks directory to the .git/hooks directory
cp infrastructure/git/hooks/pre-commit.sh .git/hooks/pre-commit
# Make the pre-commit file executable
chmod +x .git/hooks/pre-commit
echo "Pre-commit hook added successfully"
