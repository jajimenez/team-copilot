#!/bin/bash

# Team Copilot - Boostrap Installer
#
# This script downloads the latest version of Boostrap from the official Bootstrap
# repository to a given directory.
#
# Usage: ./install-bootstrap.sh <directory>
# Example: ./install-bootstrap.sh static/

# Check if the directory argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Check if the provided argument is a valid directory
if [ ! -d "$1" ]; then
    echo "\"${1}\" is not a valid directory."
    exit 1
fi

# Paths
BS_TMP_FILE="bootstrap-dist.zip"
BS_IC_TMP_FILE="bootstrap-icons-dist.zip"
BS_OUT_DIR="$1"/bootstrap
BS_IC_OUT_DIR="$1"/bootstrap-icons

# Check if any of the output directories exist and quit if it does
if [ -d "$BS_OUT_DIR" ]; then
    echo "\"${BS_OUT_DIR}\" already exists. Please remove it before running this script."
    exit 1
fi

if [ -d "$BS_IC_OUT_DIR" ]; then
    echo "\"${BS_IC_OUT_DIR}\" already exists. Please remove it before running this script."
    exit 1
fi

# Check if the temporary files exist and remove them if they do
if [ -f "$BS_TMP_FILE" ]; then
    rm "$BS_TMP_FILE"
fi

if [ -f "$BS_IC_TMP_FILE" ]; then
    rm "$BS_IC_TMP_FILE"
fi

# Create the output directories
mkdir -p "$BS_OUT_DIR"
mkdir -p "$BS_IC_OUT_DIR"

# Get the latest Bootstrap version number
BS_VERSION=$(curl -s https://api.github.com/repos/twbs/bootstrap/releases/latest | grep -Po '"tag_name": "v\K[^"]*')

# Download the Bootstrap distribution ZIP file
echo "Downloading Bootstrap version ${BS_VERSION} to ${BS_OUT_DIR}..."
echo

curl -L "https://github.com/twbs/bootstrap/releases/download/v${BS_VERSION}/bootstrap-${BS_VERSION}-dist.zip" -o "$BS_TMP_FILE"

# Get the latest Bootstrap Icons version number
BS_IC_VERSION=$(curl -s https://api.github.com/repos/twbs/icons/releases/latest | grep -Po '"tag_name": "v\K[^"]*')

# Download the Bootstrap Icons distribution ZIP file
echo "Downloading Bootstrap Icons version ${BS_IC_VERSION} to ${BS_IC_OUT_DIR}..."
echo

curl -L "https://github.com/twbs/icons/releases/download/v${BS_IC_VERSION}/bootstrap-icons-${BS_IC_VERSION}.zip" -o "$BS_IC_TMP_FILE"

# Extract the files to the output directories
unzip "$BS_TMP_FILE" -d "$BS_OUT_DIR"
unzip "$BS_IC_TMP_FILE" -d "$BS_IC_OUT_DIR"

# Clean up
rm "$BS_TMP_FILE"
rm "$BS_IC_TMP_FILE"
echo
echo "Done."
