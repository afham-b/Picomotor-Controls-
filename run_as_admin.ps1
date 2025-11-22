# Variables
$deviceInstanceId = "USB\\VID_104D&PID_4000\\12345678"

# Function to disable the device
function Disable-Device {
    param (
        [string]$DeviceId
    )
    $device = Get-PnpDevice | Where-Object { $_.InstanceId -eq $DeviceId }
    if ($device.Status -eq "OK") {
        Disable-PnpDevice -InstanceId $DeviceId -Confirm:$false
        Write-Host "Device disabled."
    } else {
        Write-Host "Device is already disabled."
    }
}

# Function to enable the device
function Enable-Device {
    param (
        [string]$DeviceId
    )
    $device = Get-PnpDevice | Where-Object { $_.InstanceId -eq $DeviceId }
    if ($device.Status -ne "OK") {
        Enable-PnpDevice -InstanceId $DeviceId -Confirm:$false
        Write-Host "Device enabled."
    } else {
        Write-Host "Device is already enabled."
    }
}

# Disable and then Enable the device
# Enable-Device -DeviceId $deviceInstanceId
Start-Sleep -Seconds 1
Disable-Device -DeviceId $deviceInstanceId
Start-Sleeo -Seconds 10
# Start-Sleep -Seconds 1
Enable-Device -DeviceId $deviceInstanceId
Start-Sleeo -Seconds 10
