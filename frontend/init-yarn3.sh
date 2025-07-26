#!/bin/bash
# Initialize Yarn 3 for the frontend project

echo "Initializing Yarn 3..."

# Enable corepack if not already enabled
corepack enable

# Set Yarn version to 3.2.3
yarn set version 3.2.3

# Ensure nodeLinker is set to node-modules
if ! grep -q "nodeLinker:" .yarnrc.yml 2>/dev/null; then
    echo "nodeLinker: node-modules" >> .yarnrc.yml
fi

echo "Yarn 3 initialized successfully!"
echo "You can now run 'docker-compose build frontend' to build the Docker image."