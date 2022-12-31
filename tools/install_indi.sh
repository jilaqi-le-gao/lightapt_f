function install_indi_ubuntu(){
    # Install INDI library on Ubuntu
    # Use the official package
    echo "Installing INDI library on Ubuntu"
    echo "Use the official package on ppa"
    sudo apt-add-repository ppa:mutlaqja/ppa
    sudo apt-get update
    sudo apt-get install indi-full gsc kstars-bleeding
}

function install_indi_debian(){
    # Install INDI library on Debian
    # Use Astroberry source
    wget -O - https://www.astroberry.io/repo/key | sudo apt-key add -
    sudo su -c "echo 'deb https://www.astroberry.io/repo/ buster main' > /etc/apt/sources.list.d/astroberry.list"
    sudo apt-get update
    sudo apt-get install indi-full gsc kstars-bleeding
}

function install_indi_centos(){
    # Install INDI library on Centos
    sudo dnf copr enable xsnrg/kstars-bleeding
    sudo dnf copr enable xsnrg/stellarsolver-bleeding
    sudo dnf copr enable xsnrg/libindi-bleeding
    sudo dnf copr enable xsnrg/indi-3rdparty-bleeding
    sudo dnf copr enable xsnrg/ekosdebugger

    sudo dnf install indi-*
    sudo dnf install kstars
}

function install_indi_source(){
    # Install INDI library from source
    sudo apt-get install -y   git   cdbs   dkms   cmake   fxload   libev-dev   libgps-dev   libgsl-dev   libraw-dev   libusb-dev   zlib1g-dev   libftdi-dev   libgsl0-dev   libjpeg-dev   libkrb5-dev   libnova-dev   libtiff-dev   libfftw3-dev   librtlsdr-dev   libcfitsio-dev   libgphoto2-dev   build-essential   libusb-1.0-0-dev   libboost-regex-dev   libcurl4-gnutls-dev   libtheora-dev
    git clone --depth 1 https://github.com/indilib/indi.git
    cd indi
    mkdir build && cd build
    cmake -DCMAKE_INSTALL_PREFIX=/usr ..
    make -j$(nproc)
    sudo make install
}

function install() {
    # Check system version
    if [[ -n $(find /etc -name "redhat-release") ]] || grep </proc/version -q -i "centos"; then
        # Get centos version
        centosVersion=$(rpm -q centos-release | awk -F "[-]" '{print $3}' | awk -F "[.]" '{print $1}')
        if [[ -z "${centosVersion}" ]] && grep </etc/centos-release "release 8"; then
            centosVersion=8
        fi
        release="centos"
        install_indi_centos
    elif grep </etc/issue -q -i "debian" && [[ -f "/etc/issue" ]] || grep </etc/issue -q -i "debian" && [[ -f "/proc/version" ]]; then
        if grep </etc/issue -i "8"; then
            debianVersion=8
        fi
        release="debian"
        install_indi_debian
    elif grep </etc/issue -q -i "ubuntu" && [[ -f "/etc/issue" ]] || grep </etc/issue -q -i "ubuntu" && [[ -f "/proc/version" ]]; then
        release="ubuntu"
        install_indi_ubuntu
    fi

    if [[ -z ${release} ]]; then
        echo "Unknown system"
        install_indi_source
    else
        echo "Current system is ${release}"
    fi
}

function check_root(){
    if [ `whoami` != 'root' ];then
        echo "Please run in root mode"
        exit 1
    fi
}

check_root

echo "Auto installation of INDI library"
echo "Written by Max Qian"
echo "Version : 1.0.0"

echo "Update and upgrade all of the softwares"
sudo apt-get update
sudo apt-get upgrade
echo "Finished upgrading all of the softwares"

install

echo "Installing all of the INDI packages successfully" 