#!/bin/bash

# TaxAI Git Repository Initialization Script

# Exit on error
set -e

# Function to display status messages
print_status() {
    echo -e "\n\033[1;34m$1\033[0m"
}

# Function to display success messages
print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "\033[1;31mGit is not installed. Please install git first.\033[0m"
    exit 1
fi

# Initialize git repository if .git directory doesn't exist
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Add all files to git
print_status "Adding files to Git..."
git add .

# Initial commit
print_status "Creating initial commit..."
git commit -m "feat: Initial project setup"

# Create develop branch
print_status "Creating develop branch..."
git branch develop
print_success "Develop branch created"

print_status "Switching to develop branch..."
git checkout develop
print_success "Now on develop branch"

print_success "Git repository setup complete!"
print_status "Next steps:"
echo "1. Create a remote repository (e.g., on GitHub, GitLab)"
echo "2. Add the remote repository: git remote add origin <repository-url>"
echo "3. Push the code: git push -u origin develop"
echo "4. Push the main branch: git checkout main && git push -u origin main"
