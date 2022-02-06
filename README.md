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

## Few notable features

- Supports windows and linux victims
- Docker support
- Evil stuff/modules you can do/run on your victim :
	- Taking Screenshots
	- Taking out Browser History
	- See the running processes
	- File download/exfiltration
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
	sudo docker exec -it spyderc2_server python3 /home/attacker/SpyderC2/main.py
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



## Progress

- Previously
	- Running the program will make a stager exe, start a server. The actual files in the directory where the stager.exe is run will be passed to the C2 server.
	- The flask server now runs as a separate process and the server is killed whenever the main script exits.
	- The stager now beacons continuously for commands, when commands given it sends all files in current directory
	- Added mongodb for communication between server and main script.
	- Victim now sends identifier as b64 cookie, server stores in  victims collection.

- 08.08.2021
	- Now victim goes through staging phase, where it gives OS info(STAGE-0) to server
	- In stage 0, server responds with 200 OK menaing successful staging, 302 meaning Victim already registered and 400 for bad request. If 200 OK recieved then it will move on to beaconing
	- Server UI now has use command to interact with a victim, where new victim specific commands can be issued
	- Added info command for victim to show the victim ID and OS info.

- 13.08.2021
	- Now the victim has a last seen and a DEAD or alive status shown with the info command.
	- The time after which victim is considered dead is 60 secs

- 12.09.2021
	- Added modules for powershell and python browser_history and screenshot
	- Linux screenshot and windows browser history works right now.

- 18.09.2021
	- All the modules (screenshot and browser_history) of python and powershell works
	- Task now has a ID, Task is no more deleted, instead has a issued flag.
	- Task output is added to the same task in db, task status is viewable in victim menu using tasks command.
	- On the stager side if issue in handling commands, traceback is sent back in a GET request

- 07.10.2021
	- Converted from procedural to object oriented.
	- Victim can now be interacted with part of the ID

- 10.10.2021
	- Introduced logger for the framework
	- Added command history like bash using readline
	- the log.txt now shows useful logs like new victim joined, or task issued
	- log is now opened autpmatically in a new terminal when main script is invoked. Needs Gnome-terminal

- 12.10.2021
	- Modules now have their own classes.
	- Both Powershell and python script are now present as string in their respective module_name classes which are subclasses of Module

- 04.11.2021
	- Kill victim
	- Modules are parametrized
	- Can't send command if victim dead
	- Task status updated from DB before showing info
	- Victim now shows if admin privileges present with info command

- 07.11.2021
	- Added exfiltration module
	- Module script can now be modified as per user provided options before sending
	- On victim side, script file is saved as command_taskid to avoid conflict

- 01.01.2022
	- No console on stager execution

- 02.01.2022
	- Added running process module
	- Stager now removes the script it creates

- 16.01.2022
	- Added docker support
	- Moved all files to data folder for easiness with docker
	- Server URL is now replaced in stager
	- Added Ascii art
	- Some help text improvements

- 19.01.2022
	- Minor fixes here and there
	- Added instructions on how to use

- 20.01.2022
	- Added -d flag to not launch logs automatically
	- Proper checking of whether listener is preocupied or not
	- listener can now be launched at any port. Port range for docker limited to 8080-8100 due to increased docker up times in case huge amount of ports forwarded. Can be changed from docker-compose.yml
	- Added capabiltity to kill the process if port is already occupied (Not for docker)
	- Stager generation for linux
	- Language for module now configureable

- 30.01.2022
	- Added support of packer, to pack the stager. Helps with it not being detected as malicious.

- 04.02.2022
	- Added location of stager as one of the info returned initially.
	- Added a persistence module - Registrykey (Powershell and python). Also utility is not hardcoded.
	- Prettified input a bit

- 06.02.2022
	- Victim ID now not random, instead part of a hash which identifies a victim
	- Victims can now re-register (if server or victim dies)
	- Clearing database on exit/error is now optional with -c flag
	- Fixed few issues
	- DB in docker now consistent


## For **FUTURE**

- Major

	- http payload encryption
	- TLS
	- New modules
		- upload files
		- dialog box popup for creds
		- keylogger
		- Registry Manipulation
		- Process running
		- Persistence
		- shell
	- Unit test
		- Server starts
		- Modules


- Medium

	- Funny names of victims and meaningful victim ID
	- Debug mode for the stager
	- Reregister victim if server stopped and then started, but victim still beaconing.
	- search module
	- Delay and Jitter
	- Write cleanup commands for modules


- Minor
	- Modules should have admin required attribute and based on that they should be allowed to execute
	- language as paramter of module
	- Check for required paramters
	- Don't send powershell command to linux victim or give warning that it might not work
	- Generate stager for linux too
	- Module description on running modules
	- Modules selectable by number or regex
