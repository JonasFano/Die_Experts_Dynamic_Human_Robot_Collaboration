#!/bin/bash

# Check if the virtual environment path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_virtual_environment>"
    exit 1
fi

# Path to the virtual environment activation script
VENV_ACTIVATE="$1/bin/activate"

# Verify if the virtual environment exists
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: Virtual environment not found at $1"
    exit 1
fi

# Paths to your Python files
FILE1="eye_tracking.py"
FILE2="safety-monitor/monitor.py"
# FILE3="safety-monitor/state_machine.py"

# Array to store process IDs (PIDs)
PIDS=()

# Function to start a script in a new terminal and track its PID
start_script() {
    local venv_activate=$1
    local working_dir=$2
    local command=$3
    gnome-terminal -- bash -c "source $venv_activate; cd $working_dir; $command; exec bash" &
    PIDS+=($!)
}

# Start each script in a new terminal
start_script "$VENV_ACTIVATE" "eye-tracking" "python $FILE1" # blinking
start_script "$VENV_ACTIVATE" "safety-monitor" "python $FILE2" # fastapi
# Uncomment the following line to run the state machine script
# start_script "$VENV_ACTIVATE" "safety-monitor" "python $FILE3"

# Function to terminate all processes
terminate_processes() {
    echo "Terminating all scripts..."
    for pid in "${PIDS[@]}"; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid
            echo "Killed process with PID $pid"
        else
            echo "Process with PID $pid already terminated"
        fi
    done
    exit 0
}

# Monitor for 'Q' key press to terminate all processes
echo "Press 'Q' to terminate all scripts and close terminals."
while :; do
    read -rsn1 input
    if [[ $input == "q" || $input == "Q" ]]; then
        terminate_processes
    fi
done
