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
TMP_FILE="bootstrap-dist.zip"
OUT_DIR="$1"/bootstrap

# Check if the output directory exists and quit if it does
if [ -d "$OUT_DIR" ]; then
    echo "\"${OUT_DIR}\" already exists. Please remove it before running this script."
    exit 1
fi

# Check if the temporary file exists and remove it if it does
if [ -f "$TMP_FILE" ]; then
    rm "$TMP_FILE"
fi

# Create the output directory
mkdir -p "$OUT_DIR"

# Get the latest version number
BOOTSTRAP_VERSION=$(curl -s https://api.github.com/repos/twbs/bootstrap/releases/latest | grep -Po '"tag_name": "v\K[^"]*')

# Download the compiled distribution ZIP file
echo "Downloading Bootstrap version ${BOOTSTRAP_VERSION} to ${OUT_DIR}..."
echo

curl -L "https://github.com/twbs/bootstrap/releases/download/v${BOOTSTRAP_VERSION}/bootstrap-${BOOTSTRAP_VERSION}-dist.zip" -o "$TMP_FILE"

# Extract the files to the output directory
unzip "$TMP_FILE" -d "$OUT_DIR"

# Clean up
rm "$TMP_FILE"
echo
echo "Done."
