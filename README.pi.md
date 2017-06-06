2017/01/17
STATUS: BETA operational local

Rasberry Pi basisbundel (incl behuizing, 2.5 A adapter, 16 GB micro card) € 65,-
Lunix versie Jessie
Power on with screen: change this if needed via raspi-config

FIRST: make a backup of the micro mem card on your desktop. So you can roll back.

HEADLESS Pi
No console no screen to the Pi well no problem.
Power on the Pi. Make sure the Pi is connected with a cable to your router.
Try to find the IP address eg via the command "arp -n" something as 192.168.0.34
Connect via ssh: ssh pi@192.168.0.34 use deflt password raspberry
If you are heading for a wireless (wifi) Pi? You have to set up some configuration
on the SD first: see http://dougbtv.com/2016/03/06/raspi-3-headless-wifi/

FIRST UPGRADE
You need for this to have an internet connection.
You probably do not need the package wolfram-engine (680 MB) so delete the package:
    sudo apt-get purge wolfram-engine
Startup and perform an upgrade:
    sudo apt-get update     # update package info
    sudo apt-get -y upgrade # upgrade all packages
    sudo apt-get dist-upgrade       # upgrade to latest system packages
    sudo apt-get autoremove # remove packages not longer needed

FIRST CONFIG
initiate/command: sudo raspi-config
expand filesystem if one created new PI OS on mem card.
for now enable start with screen (disable this later)
localisation options:
    set language eg to nl_NL.UTF-8
    set timezone eg Europe/Amsterdam
    set keyboard layout: and check by pushing @-key and see key response.
Had to edit /etc/default/keyboard the "gb" setting into "us" as well

pi% `passwd pi` -> acacadabra 
internet connectivity: sudo apt-get update/upgrade/dist-upgrade (takes a while)/autoremove
Allow to remotely login via ssh (or putty):
    sudo update-rc.d ssh enable
    sudo service ssh restart

Install git for the archive downloads from eg github:
sudo apt-get install git

project name: BdP
Give the pi a nice name e.g. project name: bdp
sudo hostname bdp
sudo nano /etc/hostname and change raspberripi to bdp
Is there an internet connectivity? Try: host 8.8.8.8   # Google DNS server

INSTALL the PROJECT

Download the tar (tgz) fite or clone it from github (sudo git clone https://github.com/IoS)
Via tar:
Copy the MySense.tgz into the pi user home directory. Unpack the tar file (tar xzf file.tgz)
Use the INSTALL.sh shell file to install all modules.

Remote desktop:
Install vnc: sudo apt-get install tightvncserver
and start the server: tightvncserver You need to enter some passwords and remember them.
and start a session: vncserver :0 -geometry 1920x1080 -depth 24
You should be able to get a desktop from remote e.g. Apple: start "finder" and
make sure you enabled screen share on your Apple.
Menu item: Go -> Connect to server ...  vnc://xxx.xxx.xxx.xxx

BACKDOOR
You probably want to get in touch with the node for remote management.

The following creates a backdoor to the PI via internet
ssh or if the PI is behind a firewall/router one can use simply weaved, ssh tunneling or VPN.
WEAVED
Install Weaved:
create account with weaved.com: user@host.org/acacadabra
    respond with email verify email
add names:
    name: PI_IoS-BdP_01
    SSH-Pi ssh port 28
    HTTP-Pi HTTP port 8088
Install:
    sudo apt-get install weavedconnected
    sudo vi /etc/sshd/config add port 28 and service sshd reload
    sudo weavedinstaller
    check: webbrowser login  with weaved.com login desk and push SSH-Pi: proxy/portnr
    ssh -l pi proxy??.weabevd.com -p "35757"
    sudo crontab -e and add line:
        @reboot /usr/bin/weavedstart.sh
notice: everyone with weaved password or proxy/port (and so weaved.com)
notice: and  knowing PI login/passwd can log into your PI via ssh!

or better use ssh tunneling (please complete)

USERS:
Install Internet of Sense user ios (full name Internet of Sense):
sudo su
adduser ios
and add ios to sudoers list: echo "ios ALL=(ALL) PASSWD: ALL" >>/etc/sudoers.d/020_ios-passwd
and test in another window if login/sudo works for ios user before proceeding
In this home dir all MySense sources are installed.

Using github:
Install eg in IoS home dir: git clone https://github.com/...
change dir into github project name and use python setup.py install (seed REAME.md)
For python 3 use the command python3

PYTHON:
Update your Pi: sudo apt-get update
install the python installer: apt-get install python-pip
For other modules/libraries needed by the MySense.py script see README.mysense
The collection of apt-get install, pip install and github setup.py install
will install the needed modules.
Make sure you have the latest openssl: sudo apt-get install python-openssl
    

