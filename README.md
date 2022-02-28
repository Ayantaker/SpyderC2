# SpyderC2 Framework

					               (
					                )
					               (
					        /\  .-"""-.  /\
					       //\\/  ,,,  \//\\
					       |/\| ,;;;;;, |/\|
					       //\\\;-"""-;///\\
					      //  \/  C2  \/  \\
					     (| ,-_| \||/ |_-, |)
					       //`__\.-.-./__`\\
					      // /.-(() ())-.\ \\
					     (\ |)   '---'   (| /)
					      ` (|           |) `
					         \)          (/
					            SPYDERC2

## CAUTION

NOTE : This is a hobby project and is solely created for educational/learning purposes. The author/creator doesn't provide any warranty nor will take any liabilities for any damage caused due to usage of the framework.


## Few notable features

- Supports windows and linux victims
- Docker support
- Not detectable by antiviruses
- Evil stuff/modules you can do/run on your victim :
	- Taking Screenshots
	- Taking out Browser History
	- See the running processes
	- File download/exfiltration
	- Persistence
	- Reverse shell
- New modules are easy to write and integrate
- No window pops up when stager is executed on victim.


## Installation

- It's much easier to use the docker version to not run into dependency issues.
- Install Docker for your distro
- Get Docker Compose from [here](https://docs.docker.com/compose/install/)
- Now simply run :

	```bash
	sudo docker-compose up
	```
- Once the 2 containers spins up (Python and MongoDB), run the following :

	```bash
	sudo docker exec -it server python3 /home/attacker/SpyderC2/main.py
	````

- You should be greeted with SpyderC2 server console. Now follow the below steps to try out the framework


## How to use:

- First run a listener, by running http. Check in the logs if the listener is started successfully.

- Then you would want to generate a payload/stager , by running generate command. Enter your host IP address when server URL is asked. If you are running on your host machine, it will be generated automatically, if running on docker, you would get a help text to generate the stager.

- Then copy this stager.exe to the victim Windows machine.

- Double click the stager.exe on the victim. You should see a new victim with an ID in logs.

- Check the vicitm list using 'vicitms' command.

- To do evil stuff on victim, run 'use <victim_id>'.

- Now you are in victim help menu. Run 'modules' to see the stuff you can run on teh victim.

- To run a module, use <module_name> , ex : use screenshot.

- You can then modify the arguments available for that module, Ex , you can set the path where screenhsot will be saved on the attacker/host machine, using 'set path /home'. It's optional as by default they will be stored in victim/<victim_id> folder.

- Now to run this module on victim, execute - 'run'

- Check in the logs you will see the script/task bein issue to the victim, and logs will also show where the output/screenshot is being stored.



## Wiki Pages

- A look at the various chnagelogs / progress in the framework : https://github.com/Ayantaker/SpyderC2/wiki/changelog

- Future Work : https://github.com/Ayantaker/SpyderC2/wiki/Future-Work
