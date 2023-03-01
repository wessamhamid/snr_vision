#! /bin/bash

#this script is for controller and bluetooth initialization


controller_check=false
password=kouseigaku



bluetooth_controller() {

    MAC=84:30:95:8B:4C:15

    ds4drv > /dev/null 2>&1 &

    echo "waiting for ps4 controller to be connected ...."

    while bluetoothctl info $MAC | grep -q "Connected: no"
    do
        if bluetoothctl info $MAC | grep -q "Connected: yes";
        then
            echo "PS4 controller connected"
            #controller_check = true

            break
        fi

    done
}

clr_ds4drv(){
    pkill ds4drv
    echo "Cleaning up....."
}


motor_initialization(){

    if ip link show | grep -q "can0: <NOARP,ECHO> mtu 16 qdisc noop state DOWN mode DEFAULT group default qlen 10";
    then
        echo "can0 detected"
        echo "initializing motors........"
        echo $password | sudo -S ip link set can0 type can bitrate 1000000
        sleep 2
        sudo ifconfig can0 txqueuelen 10000
        sleep 2
        sudo ip link set up can0
        sleep 2
        echo "excute order 69..."
    fi

}


bluetooth_controller 
motor_initialization
sleep 2
roslaunch inspecto_base snr_startup.launch >/dev/null 2>&1 &
sleep 2
roslaunch ps4_ros snr_joystick.launch
clr_ds4drv
# if bluetooth_controller
# echo "robot ready to use !!!!"

# while true;


# bla= bluetoothctl devices | awk '{print $2}'

# echo $bla
# echo $bla

# if [[ $bla == "84:30:95:8B:4C:15" ]]; 
# then
#     echo "bluetooth controller connected"
# fi
