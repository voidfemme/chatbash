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
cp "$program_file" "/usr/local/bin/$program_name"
chmod +x "/usr/local/bin/$program_name"

# Copy the man page to /usr/local/share/man/man1 and set the read permission
mkdir -p "/usr/local/share/man/man1"
cp "$man_page" "/usr/local/share/man/man1/"
chmod +r "/usr/local/share/man/man1/$man_page"

# Update the man database
mandb

echo "Installation complete. You can now run 'chatbash' from the command line"
