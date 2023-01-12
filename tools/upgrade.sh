#!/bin/bash
export PATH

# Check if user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script"
    exit 1
fi

cur_dir=$(pwd)
action=$1
shopt -s extglob
Upgrade_Date=$(date +"%Y%m%d%H%M%S")

Get_Dist_Name
MemTotal=`free -m | grep Mem | awk '{print  $2}'`

Display_Upgrade_Menu()
{
    echo "1: Upgrade Kstars"
    echo "2: Upgrade PHD2"
    echo "3: Upgrade astap"
    echo "4: Upgrade python and dependencies"
    echo "5: Upgrade all of the softwares"
    echo "exit: Exit current script"
    echo "###################################################"
    read -p "Enter your choice (1, 2, 3, 4, 5 or exit): " action
}

clear
echo "+-----------------------------------------------------------------------+"
echo "|          Upgrade script for LightAPT , written by Max Qian            |"
echo "+-----------------------------------------------------------------------+"
echo "|       A tool to upgrade astronomy software like kstars or phd2        |"
echo "+-----------------------------------------------------------------------+"

if [ "${action}" == "" ]; then
    Display_Upgrade_Menu
fi

    case "${action}" in
    1|[kK][sS][tT][aA][rR][sS])
        sudo apt update && sudo apt install kstars -y
        ;;
    2|[pP][hH][dD][2])
        sudo apt update && sudo apt install phd2 -y 
        ;;
    3|[aA][sS][tT][aA][pP])
        sudo apt update && sudo apt install astap -y
        ;;
    4|[pP][yY][tT][hH][pO][nN])
        sudo apt update && sudo apt install python3 -y
        ;;
    5|[aA][lL][lL])
        sudo apt update && sudo apt upgrade -y
        ;;
    [eE][xX][iI][tT])
        exit 1
        ;;
    *)
        echo "Usage: ./upgrade.sh {kstars|phd2|astap|python|all}"
        exit 1
    ;;
    esac