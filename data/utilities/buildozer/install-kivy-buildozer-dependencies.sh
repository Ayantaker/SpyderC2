#!/bin/bash
## Taken from https://github.com/HeaTTheatR/KivyMD-data/raw/master/install-kivy-buildozer-dependencies.sh

# Install Python pip
if [ -e /usr/bin/apt ]; then
	sudo apt-get install -y curl
	sudo apt-get install -y python3-distutils
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	sudo python3 get-pip.py

	# Dependencies with SDL2
	# Install necessary system packages
	sudo apt-get install -y \
    	python-pip \
    	build-essential \
    	git \
    	python \
    	python3-dev \
    	ffmpeg \
    	libsdl2-dev \
    	libsdl2-image-dev \
    	libsdl2-mixer-dev \
    	libsdl2-ttf-dev \
    	libportmidi-dev \
    	libswscale-dev \
    	libavformat-dev \
    	libavcodec-dev \
    	zlib1g-dev
elif [ -e /usr/bin/pacman ]; then
	sudo pacman -Syu #make sure repos are up to date and no partial upgrades occur 
	sudo pacman -S --noconfirm curl python-distutils-extra python-pip
	sudo pacman -S --noconfirm base-devel python ffmpeg sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi zlib
else
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	sudo python3 get-pip.py
fi
# Dependencies Kivy
sudo pip3 install cython

# Install Kivy
sudo pip3 install kivy

# Dependencies Buildozer
if [ -e /usr/bin/apt ]; then
	sudo apt install -y \
    	build-essential \
    	ccache \
    	git \
    	libncurses5:i386 \
    	libstdc++6:i386 \
    	libgtk2.0-0:i386 \
    	libpangox-1.0-0:i386 \
    	libpangoxft-1.0-0:i386 \
    	libidn11:i386 \
    	python2.7 \
    	python2.7-dev \
    	openjdk-8-jdk \
    	unzip \
    	zlib1g-dev \
    	zlib1g:i386 \
    	libltdl-dev \
    	libffi-dev \
    	libssl-dev \
    	autoconf \
    	autotools-dev \
    	cmake
fi
if [ -e /usr/bin/pacmann ]; then
	#this requeires the multilib repo to be enabled
	sudo pacman -S --noconfirm base-devel ccahe git ncurses lib32-ncurses libstdc++5 gtk2 lib32-gtk2 lib32-pango lib32-libidn11  jdk8-openjdk unzip zlib lib32-zlib lib32-libltdl libffi openssl autoconf cmake
fi
# Install Buildozer
git clone https://github.com/kivy/buildozer.git
cd buildozer || return 1
sudo python3 setup.py install
