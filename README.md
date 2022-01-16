**This is the beginning of a python based C2 framework**

## Initial Goal
- Have a python based stager which when executed on windows will give out the current directory information.
- Have a python based http listener, which will print the information


## Current Condition
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

- 16.01.2020
	- Added docker support
	- Moved all files to data folder for easiness with docker
	- Server URL is now replaced in stager


## **FUTURE** Feature Additions

- Major

	- Modules to be modular. Plug and play
	- http payload encryption
	- TLS
	- New modules
		- upload files
		- dialog box popup for creds
		- keylogger
		- Registry Manipulation
		- Process running
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


## Note for next time dev
 - Add comments to all parts of code
 - RC checking for os commands