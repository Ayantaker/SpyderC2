FROM python:3.8.12-alpine3.15

RUN pip3 install termcolor ## These can be made into requirements.txt which python container auto install??
RUN pip3 install pymongo
RUN pip3 install flask
## better to do with docker compose volume ?
COPY data /SpyderC2 

# CMD ["/usr/local/bin/python3" , "/SpyderC2/main.py"]

## TO keep the conatiner running, and also if the main Spyder program crashes, container will not go down
CMD ["tail", "-f" ,"/SpyderC2/logs/logs"]


