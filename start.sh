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

echo "Installing/upgrading requirements from $REQUIREMENTS_FILE..."

handle_version_mismatch() {
    local package_name=$1
    local installed_version=$(pip show $package_name | grep Version | awk '{print $2}')
    local required_version=$(grep "$package_name" $REQUIREMENTS_FILE | cut -d'=' -f3)

    if [ "$installed_version" == "$required_version" ]; then
        echo "Version matches for $package_name: $installed_version"
    elif [ "$(printf '%s\n' "$installed_version" "$required_version" | sort -V | head -n1)" == "$installed_version" ]; then
        echo "Installed version of $package_name ($installed_version) is newer. Uninstalling and reinstalling..."
        pip uninstall -y $package_name
        pip install $package_name
    else
        echo "Installed version of $package_name ($installed_version) is older. Upgrading..."
        pip install --upgrade $package_name
    fi
}

while IFS= read -r line; do
    package=$(echo $line | cut -d'=' -f1)
    handle_version_mismatch $package
done < $REQUIREMENTS_FILE

echo "Starting $MAIN_SCRIPT..."
python $MAIN_SCRIPT tee /dev/tty

deactivate
