#!/bin/bash

# Set necessary variables
program_name="chatbash"
program_file="chatbash.py"
man_page="chatbash.1"

# Check if the user is running the script as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Please run the installation script as root or with sudo:"
    echo "  sudo ./install.sh"
    exit 1 
fi

# Copy the program to /usr/local/bin and set the executable permission
echo "Copying program..."
cp "$program_file" "/usr/local/bin/$program_name"
chmod +x "/usr/local/bin/$program_name"

# Copy the man page to /usr/local/share/man/man1 and set the read permission
echo "Copying man page..."
mkdir -p "/usr/local/share/man/man1"
cp "docs/$man_page" "/usr/local/share/man/man1/"
chmod +r "/usr/local/share/man/man1/$man_page"

# Update the man database
echo "Updating man database..."
mandb -q

# Check if the program file installation was successful
echo "Checking program file installation..."
if [ -x "/usr/local/bin/$program_name" ]; then
    echo "Program file installed successfully."
else
    echo "Program file installation failed. Please check the script and try again."
    exit 1 
fi

# Check if the man page file installation was successful
echo "Checking man page file installation..."
if [ -r "/usr/local/share/man/man1/$man_page" ]; then
    echo "Man page file installed successfully. You can now run 'chatbash' from the command line."
else
    echo "Man page file installation failed. Please check the script and try again."
    exit 1 
fi

