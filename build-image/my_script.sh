#!/usr/bin/env bash


# no hup running dockerd in background
nohup sudo dockerd &


# pull the images and start container in docker in container
./launch_binary_linux \
    --user_id=$USER_ID \
    --device_id=$DEVICE_ID \
    --device_name=$DEVICE_NAME \
    --operating_system="Linux" \
    --usegpus=true


# command to keep the main process alive
tail -f /dev/null
