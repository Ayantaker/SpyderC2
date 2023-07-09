FROM amd64/ubuntu:20.04
RUN apt-get update

## DEBIAN_FRONTEND=noninteractive added as installation was getting stuck asking for some user input. Most of the libnraries expect python and pip is needed for android stager generation
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential libssl-dev curl sudo git default-jre default-jdk unzip autoconf pkg-config libffi-dev libtool python3 python3-pip zip docker.io

RUN pip3 install termcolor pymongo flask rich

COPY data /home/attacker/SpyderC2
WORKDIR /home/attacker/SpyderC2

## TO keep the conatiner running, and also if the main Spyder program crashes, container will not go down
CMD ["tail", "-f" ,"/home/attacker/SpyderC2/logs/logs"]


