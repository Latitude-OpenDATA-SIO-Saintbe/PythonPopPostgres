#!/bin/bash

# Define the desired path
BASE_PATH="$1"

# Check if a path was provided
if [ -z "$BASE_PATH" ]; then
  BASE_PATH="."
fi

# List of Python scripts to run
python_scripts=("DB-create.py" "DB-fake-seed.py")  # Add your Python scripts here

# Step 1: Install required Python libraries
echo "Installing required Python libraries..."
pip install psycopg2-binary python-dotenv requests

# Step 2: Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "Libraries installed successfully!"
else
    echo "Error installing libraries. Please check your environment."
    exit 1
fi

# Step 3: Loop through the list of Python scripts and run each one
for script in "${python_scripts[@]}"; do
    echo "Running $script..."
    python "$BASE_PATH/$script"

    # Check if the Python script ran successfully
    if [ $? -eq 0 ]; then
        echo "$script ran successfully!"
    else
        echo "Error running $script. Exiting."
        exit 1
    fi
done
