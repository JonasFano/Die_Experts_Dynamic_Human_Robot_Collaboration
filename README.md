# Die_Experts_Dynamic_Human_Robot_Collaboration
Project in the Expert in Teams course in the 3rd Master's semester at SDU



How to create connection to the robot using usb-c hub:
- ip link
- sudo ifconfig enx207bd259e802 192.168.1.101 up
- Note: sudo ifconfig >name_of_network_shown_in_ip_link< >desired_ip_adress< up


If running the code in a python venv (using the following command: sudo apt install python3.11-venv)
- source /home/jonas/ur5e/bin/activate
- python3 /home/jonas/Downloads/Die_Experts_Dynamic_Human_Robot_Collaboration/EiT_demo.py


Hypotheses:
- Waiting for the fixture to be full before moving the robot reduces/increases the workers stress level compared to gradually moving the parts to the tray as the come in.
- Adjusting robot speed based on distance to human workers using human body pose estimation. 
    - Does giving the human workers control over the robot speed reduces their stress level?
- Eye-tracking of the human worker
    - Does the human workers do more rapid eye movements if they are stressed? (look in literature) 
    - Does the human workers look more often at the robot if they are stressed?
    - Reducing the speed of the robot based on the eye movement of the human worker reduces their stress level.
- Optional: Give the robot eyes
    - The stress level is reduced if the robot closes its eyes while waiting compared to looking with open eyes at the human worker.


Literature
- Stress level
- Worker stress management
- Reducing stress in production
- Robot based production stress
- Eye-movement when stressed
- Worker tracking