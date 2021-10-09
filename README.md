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
	- Added command history like bash using realine
	- the log.txt now shows useful logs like new victim joined, or task issued
	- log is now opened autpmatically in a new terminal when main script is invoked. Needs Gnome-terminal



## Add these
- Status of victim whether dead or alive
- Show on main screen, new victim has joined
- Cant send commands if dead
- Kill victim
- Funny names of victims
- Modules to be modular. Plug and play
- Idenitfication of admin privelges
- Debug mode for the stager
- Reregister victim if server stopped and then started, but victim still beaconing



## Note for next time dev

- Fix the modules
- Return from the powershell screenshot not proper