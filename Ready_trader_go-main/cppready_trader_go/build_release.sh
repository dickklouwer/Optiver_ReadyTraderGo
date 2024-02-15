#!/bin/bash

# Check if executable name was provided
if [ $# -eq 0 ]; then
  echo "Please provide the executable name as an argument."
  exit 1
fi

# Set executable name and JSON file name
EXECUTABLE_NAME=$1
JSON_FILE_NAME="${EXECUTABLE_NAME}.json"

# Build the executable
cmake -DCMAKE_BUILD_TYPE=Release -B build && cmake --build build --config Release

# Check if building succeeded
if [ $? -eq 0 ]; then
  # Rename and copy executable
  cp build/autotrader "${EXECUTABLE_NAME}"

  # Copy JSON file if it doesn't exist
  if [ ! -f "${JSON_FILE_NAME}" ]; then
    cp autotrader.json "${JSON_FILE_NAME}"
  fi
else
  echo "Error building executable."
  exit 1
fi
