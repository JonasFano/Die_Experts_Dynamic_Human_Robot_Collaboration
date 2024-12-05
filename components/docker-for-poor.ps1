# Check if the virtual environment path is provided
param (
    [string]$VenvPath
)

if (-not $VenvPath) {
    Write-Host "Usage: .\run_and_manage_processes.ps1 -VenvPath <path_to_virtual_environment>"
    exit
}

# Path to the virtual environment activation script
$venvActivate = Join-Path $VenvPath "Scripts\Activate"

# Verify if the virtual environment exists
if (-not (Test-Path $venvActivate)) {
    Write-Host "Error: Virtual environment not found at $VenvPath"
    exit
}

# Paths to your Python files
$file1 = "eye_tracking.py"
$file2 = "safety-monitor/monitor.py"
# $file3 = "safety-monitor/state_machine.py"

# Array to store process information
$processes = @()

# Function to start a new process and track it
function Start-Script {
    param (
        [string]$venvActivatePath,
        [string]$workingDir,
        [string]$command
    )

    $fullCommand = "& $venvActivatePath; cd $workingDir; $command"
    $process = Start-Process powershell -ArgumentList "-NoExit", "-Command", $fullCommand -PassThru
    return $process
}

# Start each script in a new terminal
$processes += Start-Script -venvActivatePath $venvActivate -workingDir "eye-tracking" -command "python $file1" # blinking
$processes += Start-Script -venvActivatePath $venvActivate -workingDir "safety-monitor" -command "python $file2" # fastapi
# $processes += Start-Script -venvActivatePath $venvActivate -workingDir "safety-monitor" -command "python $file3"

# Monitor for 'Q' key press to terminate all processes
Write-Host "Press 'Q' to terminate all scripts and close terminals."

while ($true) {
    if ([console]::KeyAvailable) {
        $key = [console]::ReadKey($true)
        if ($key.Key -eq "Q") {
            Write-Host "Terminating all scripts..."
            foreach ($process in $processes) {
                try {
                    if ($process -and $process.HasExited -eq $false) {
                        # Kill the entire process tree
                        Stop-Process -Id $process.Id -Force
                    }
                } catch {
                    Write-Host "Failed to terminate process with ID $($process.Id). It may have already exited."
                }
            }
            break
        }
    }
    Start-Sleep -Milliseconds 100
}
