# Components
This folder contains all of the components for the project. 

Each python component can be run using `python -m <folder_name.file_name>` from this dir. 

To import files from other modules you use relative paths. `..module_name.filename` for importing from a module from parent folder.


Modules:
- `safety_monitor` - Handles all of the realsense related calculations.
- `socket_robot_controller` - Is a SocketIO layer on top of the 