#!/bin/sh

# This script starts the Ollama server, waits for it to be ready and pulls the needed Ollama models.

# Check if the OLLAMA_HOST environment variable is set
if [ -z "$OLLAMA_HOST" ]; then
    echo "OLLAMA_HOST is not set"
    exit 1
fi

# Check if the EMB_MODEL environment variable is set
if [ -z "$EMB_MODEL" ]; then
    echo "EMB_MODEL is not set"
    exit 1
fi

# Check if the LLM_MODEL environment variable is set
if [ -z "$LLM_MODEL" ]; then
    echo "LLM_MODEL is not set"
    exit 1
fi

# Take the port part of the OLLAMA_HOST environment variable (e.g. "11434" from "localhost:11434")
OLLAMA_PORT=${OLLAMA_HOST#*:}

# Start Ollama in the background
echo "Starting Ollama..."
ollama serve &

# Wait for Ollama to start and be ready
until curl -s "http://localhost:${OLLAMA_PORT}/api/tags" > /dev/null 2>&1; do
    sleep 1
done

# Pull Ollama models if they haven't been pulled yet
echo "Pulling embedding model..."
ollama pull "${EMB_MODEL}"

echo "Pulling LLM model..."
ollama pull "${LLM_MODEL}"

# Wait until all background processes finish
wait
