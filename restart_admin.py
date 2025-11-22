import subprocess

# Define the task name
task_name = "Manage_Picomotor_USB"

# Call the task using PowerShell
subprocess.run(["powershell", "Start-ScheduledTask", "-TaskName", task_name])

# Alternatively, using schtasks command
# subprocess.run(["schtasks", "/Run", "/TN", task_name])
