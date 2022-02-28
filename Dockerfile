FROM python:3.8.12-alpine3.15

RUN pip3 install termcolor ## These can be made into requirements.txt which python container auto install??
RUN pip3 install pymongo
RUN pip3 install flask
RUN pip3 install rich



COPY data /home/attacker/SpyderC2
WORKDIR /home/attacker/SpyderC2


## TO keep the conatiner running, and also if the main Spyder program crashes, container will not go down
CMD ["tail", "-f" ,"/home/attacker/SpyderC2/logs/logs"]


