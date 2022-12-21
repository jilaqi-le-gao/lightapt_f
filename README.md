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
    
## Features
Including many useful features , and build in many powerful repositories
+ Full devices supported via ASCOM & INDI
+ Remote connection supported via noVNC
+ Small tools for image processing and star searching
+ Beautiful User interface and all platforms supported
+ Open source and stable , but also powerful

## Development
Most of the codes are written in Python and JavaScript, and we will try to add more languages to be supported. No matter what languages you are good at, just join QQ group and discuss together.

### Build
Just like the name of the project, only a few dependent libraries are needed to start

### Requirements

+ astropy
+ flask
+ numpy
+ requsets 

## Support
+ QQ Group 710622107
+ Email astro_air@126.com
