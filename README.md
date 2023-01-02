[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=AstroAir-Develop-Team_lightapt&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=AstroAir-Develop-Team_lightapt)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=AstroAir-Develop-Team_lightapt&metric=bugs)](https://sonarcloud.io/summary/new_code?id=AstroAir-Develop-Team_lightapt)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=AstroAir-Develop-Team_lightapt&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=AstroAir-Develop-Team_lightapt)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=AstroAir-Develop-Team_lightapt&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=AstroAir-Develop-Team_lightapt)

# LightAPT
Light weight and Flexible Astro Photography Terminal

## Architecture
There are two architectures both are available in LightAPT.

### Fixed Architecture
Inspired by INDI (https://github.com/indilib/indi)

    LightAPT Client 1 ----|                      |---- LightAPT Driver A  ---- Dev X
                          |                      |
    LightAPT Client 2 ----|                      |---- LightAPT Driver B  ---- Dev Y
                          |                      |                              |
            ...           |--- LightAPTserver ---|                              |-- Dev Z
                          |                      |
                          |                      |
    LightAPT Client n ----|                      |---- LightAPT Driver C  ---- Dev T


    Client       INET         Server       Driver          Hardware
    processes    websocket    process      processes       devices

### Standard Architecture
This method is likes P2P mode. Every device has its own websocket server and every client can only connect a device. This make sure that all devices can be connected flexible.

    LightAPT Client 1 <-(websocket)-> wsdevice <-(alpyca or pyindi)-> Driver 1

    LightAPT Client 2 <-(websocket)-> wsdevice <-(alpyca or pyindi)-> Driver 2

    ...

    LightAPT Client n <-(websocket)-> wsdevice <- (alpyca or pyindi)-> Driver n
    
## Features
Including many useful features , and build in many powerful repositories
+ Full devices supported via ASCOM & INDI
+ Offline skymap and virtual viewer
+ Remote connection supported via noVNC
+ Image viewer and compresser support
+ Small tools for image processing and star searching
+ Beautiful User interface and all platforms supported
+ Open source and stable , but also powerful

## Development
Most of the codes are written in Python and JavaScript, and we will try to add more languages to be supported. No matter what languages you are good at, just join QQ group and discuss together.

### Build
Just like the name of the project, only a few dependent libraries are needed to start

#### Installation

Fisrt , you should install all of the required libraries . You can run this command
"""
pip install -r requirements.txt
"""

However , when we tested this on Python3.7 , we can not install astropy from Pypi.Until now we do not find the solution to this problem.You can just ignore astropy and all of server will run normally.

#### Requirements

+ astropy(optional)
+ flask
+ flask-login
+ numpy
+ requsets 

## Support
+ QQ Group 710622107
+ Email astro_air@126.com
