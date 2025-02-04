#!/bin/bash

# Exit immediately if any command fails
set -e

# Check the Linux distribution
check_distribution () {
    if [ -f /etc/debian_version ]; then
        echo "Debian-based distribution"
        DISTRO="debian"
    elif [ -f /etc/alpine-release ]; then
        echo "Alpine-based distribution"
        DISTRO="alpine"
    else
        echo "Unsupported Linux distribution."
        DISTRO="unsupported"
        exit 1
    fi
}

# Install all the dependencies and packages required to run the application on a fresh Linux machine
install_package () {
    if [ "$DISTRO" == "debian" ]; then
        apt-get update
        apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl gnupg

        curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | apt-key add -
        echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list

        apt-get update && apt-get install -y doppler python3-virtualenv
        apt-get install -y --no-install-recommends pkg-config gcc musl-dev libmariadb-dev

    elif [ "$DISTRO" == "alpine" ]; then
        apk cache clean
        wget -q -t3 'https://packages.doppler.com/public/cli/rsa.8004D9FF50437357.key' -O /etc/apk/keys/cli@doppler-8004D9FF50437357.rsa.pub
        echo 'https://packages.doppler.com/public/cli/alpine/any-version/main' | tee -a /etc/apk/repositories
        
        apk add --no-cache doppler pkgconfig gcc musl-dev mariadb-connector-c-dev

    else
        echo "Unsupported Linux distribution."
        exit 1
    fi
}

# Install Python dependencies
install_pip () {
    if [ -f requirements.txt ]; then
        if [ "$DISTRO" == "debian" ]; then
            virtualenv .venv    # Create a virtual environment
            source .venv/bin/activate
            
            pip3 install --upgrade pip
            pip3 install --no-cache-dir -r requirements.txt

        elif [ "$DISTRO" == "alpine" ]; then
            pip3 install --upgrade pip
            pip3 install --no-cache-dir -r requirements.txt
        fi

    else
        echo "requirements.txt not found, skipping Python dependencies installation."
    fi
}

check_distribution
install_package
install_pip