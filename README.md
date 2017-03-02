# Plugin for OctoPi - For Raspberry Pi users only (Octopi) : display room temperature on navbar
# Based on OctoPrint-NavbarTemp by imrahil (https://github.com/imrahil/OctoPrint-NavbarTemp)

For Raspberry Pi users only : This plugin displays the room temperature on navbar via a ds18b20 sensor connected on pin n°4

## Setup:

Install the plugin using Plugin Manager from Settings


## Howto: Connecting your ds187b20 sensor

1 - Connecting your ds187b20 sensor to the Pi:

![Connection](raspberry-pi-ds18b20-connections.png?raw=true) 

2 - Then connect to your Octopi via ssh.

3 - we first need to open up the boot config file, this can be done by running the following command:

		sudo nano /boot/config.txt

4 - At the bottom of this file enter the following.

		dtoverlay=w1-gpio

5 - Once done save & exit by pressing ctrl x and then y. 

6 - Now reboot the Pi by running the following command.

		sudo reboot

7 - Enjoy !!

![RoomTemp](RoomTemp.png?raw=true) 

