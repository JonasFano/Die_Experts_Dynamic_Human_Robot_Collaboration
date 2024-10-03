# Die_Experts_Dynamic_Human_Robot_Collaboration
Project in the Expert in Teams course in the 3rd Master's semester at SDU



How to create connection to the robot using usb-c hub:
- ip link
- sudo ifconfig enx207bd259e802 192.168.1.101 up
- Note: sudo ifconfig >name_of_network_shown_in_ip_link< >desired_ip_adress< up


If running the code in a python venv (using the following command: sudo apt install python3.11-venv)
- source /home/jonas/ur5e/bin/activate
- python3 /home/jonas/Downloads/Die_Experts_Dynamic_Human_Robot_Collaboration/EiT_demo.py
