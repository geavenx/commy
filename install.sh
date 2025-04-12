#!/bin/bash

# Commy installation script

# Create the config directory if it doesn't exist
mkdir -p ~/.commy

# Copy the default config file if it doesn't exist
if [ ! -f ~/.commy/config.yaml ]; then
    cp default_config.yaml ~/.commy/config.yaml
    echo "Created default configuration at ~/.commy/config.yaml"
    echo "Please edit this file to add your OpenAI API key"
fi

# Install the package
pip install -e .

echo ""
echo "Installation complete! You can now use 'commy' to generate commit messages."
echo "Make sure to add your OpenAI API key to ~/.commy/config.yaml or set the COMMY_API_KEY environment variable." 