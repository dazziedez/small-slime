#!/bin/bash

VENV_DIR="./.venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="main.py"
alias python='winpty python.exe'

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating..."
    python -m venv $VENV_DIR
fi

echo "Activating virtual environment..."
source $VENV_DIR/Scripts/activate

echo "Installing requirements from $REQUIREMENTS_FILE..."
pip install -r $REQUIREMENTS_FILE

echo "Starting $MAIN_SCRIPT..."
python $MAIN_SCRIPT tee /dev/tty

deactivate
