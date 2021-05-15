**This is the beginning of a python based C2 framework**

## Initial Goal
- Have a python based stager which when executed on windows will give out the current directory information.
- Have a python based http listener, which will print the information


## Current Condition
- Running the program will make a stager exe, start a server. The actual files in the directory where the stager.exe is run will be passed to the C2 server.
- The flask server now runs as a separate process and the server is killed whenever the main script exits.
- The stager now beacons continuously for commands, when commands given it sends all files in current directory
- Added mongodb for communication between server and main script.