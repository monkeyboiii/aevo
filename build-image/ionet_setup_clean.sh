#!/bin/bash

set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
sudo dpkg --set-selections <<< "cloud-init install" || true


# Check if Docker is installed
if command -v docker &>/dev/null; then
    echo "Docker is already installed."
else
    echo "Docker is not installed. Proceeding with installations..."
    # Install Docker-ce keyring
    sudo apt update -y
    sudo apt install -y 
    sudo install -m 0755 -d /etc/apt/keyrings
    FILE=/etc/apt/keyrings/docker.gpg
    if [ -f "$FILE" ]; then
        sudo rm "$FILE"
    fi
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o "$FILE"
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker-ce repository to Apt sources and install
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release; echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update -y
    sudo apt -y install docker-ce
fi


# Check if docker-compose is installed
if command -v docker-compose &>/dev/null; then
    echo "Docker-compose is already installed."
else
    echo "Docker-compose is not installed. Proceeding with installations..."

    # Install docker-compose subcommand
    sudo apt -y install docker-compose-plugin
    sudo ln -sv /usr/libexec/docker/cli-plugins/docker-compose /usr/bin/docker-compose
    docker-compose --version
fi


# wtf
sudo apt-mark hold nvidia* libnvidia*
# Add docker group and user to group docker
sudo groupadd docker || true
sudo usermod -aG docker $USER || true
newgrp docker || true


docker run --gpus all --privileged=true \
    phantomni/ionet:latest \
    bash -c 'sudo dockerd & && ./launch_binary_linux --device_id=6e55e23f-ff3f-42a0-88f6-9188eeac20ce --user_id=57d1bc80-2582-4dca-a3bc-4551e196ccc6 --operating_system="Linux" --usegpus=true --device_name=niger'

./launch_binary_linux --device_id=6e55e23f-ff3f-42a0-88f6-9188eeac20ce --user_id=57d1bc80-2582-4dca-a3bc-4551e196ccc6 --operating_system="Linux" 