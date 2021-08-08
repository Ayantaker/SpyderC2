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



## Add these
- Status of victim whether dead or alive
- Show on main screen, new victim has joined