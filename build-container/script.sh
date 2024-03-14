# parse named args
while [ $# -gt 0 ]; do
    if [[ $1 == "--"* ]]; then
        v="${1/--/}"
        declare "$v"="$2"
        shift
    fi
    shift
done


echo $DEVICE_NAME

nohup sleep 1; echo $USER_ID > user.out &
nohup sleep 2; echo $DEVICE_ID > device.out &

tail -f /dev/null &