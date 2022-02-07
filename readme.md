# The Pi-EEPr

The world is a spooky place, and it is becoming harder to trust anyone. 
That's why we here at Rockfield Automation decided to come to market with a tool to always uncover the truth: The Pi-EEPr! 
This Remote Monitoring Tool can be used as an intruder detection system in your home or office, a passive recover for monitoring unsuspecting people, or other nefarious purposes that our legal team advised to not disclose. 
It has a microphone and camera included with modularity in mind; it then uploads those recordings to the cloud. 
The Pi-EEPr uses Discord's bot API for event notifications and configuration of the device. 
By leveraging the compute power of The Cloud, the data can assist in answering your burning questions like "Who keeps leaving my light on?" or "Why do my employees hate me?" 
In other words, you need the Pi-EEPr.

![Pi-EEPr overview](far.jpg)

## Technical instructions

To run the Pi-EEPr several specific pieces of both hardware and software are required:

- Raspberry Pi
	- Access to GPIO pins
	- DHT-11\*
	- ADXL345\*
	- Two (2) Buzzers\*
	- A Motion Sensor\*
	- A Pi-Cam\*
	- A Box\*

- Server
	- Mosquitto MQTT Server
	- Discord Server

Items with \* are optional

### Raspberry Pi

The pinouts for each IO device can be determined through looking at the cog within the RPi folder for the given device.
Pinouts may be added here at a later date.

#### Dependencies 

pip3 install -r requirements.txt
- Discord py
- gpiozero
- MqttClient

#### Running the program

(Discord instructions)

`main.py` should be ran from within the RPi folder. 
Apon startup the program will show the cogs that have started.
The ones that have failed will also get alerted.

Upon startup the accelerometer will take baseline mesurments so do not move the Pi-EEPr for the first 5 seconds.

![Pi-EEPr closeup](close.jpg)

### Discord bot setup instructions
A seperate bot should be created for the Server and RPi.
1. Go to https://discord.com/developers/applications, login and under Applications select "New Application". Give it a name.
2. Once created, go to "Bot" tab and select "Add Bot".
3. Enable "Presence Intent", "Server Members Intent", "Message Content Intent", save changes.
4. Reveal and copy the Token, you will need this later for setting up the bot code!
5. Go to Oauth2 tab, URL Generator. Select "Bot" as scope, and "Administrator" under general permissions.
6. Visit the URL generated at the bottom, add the bot to your server.
7. Your bots are set up!

### MQTT broker setup instructions (Windows)

1. Download and install Mosquitto
	https://mosquitto.org/download/ 
2. Go to directory where Mosquitto was downloaded (in powershell/cmd), create and enter username/passwords as follows:
	mosquitto_passwd -c passwd.conf <username>
3. Edit the mosquitto.conf file as follows:
	listener 1883
	allow_anonymous false
	password_file C:\<path\to\passwd\file>\passwd.conf	
4. Mosquitto is ready to rumble! Run the following command to start it with a verbose output
	mosquitto -c mosquitto.conf -v
