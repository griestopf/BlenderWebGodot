# Make sure we are running on Power Shell 7 or above. Otherwise Compress-Archive will use
# backslashes in the zip file's path names rendering the blender Add-On file invalid on 
# Linux and Mac
if ($PSVersionTable.PSVersion.Major -lt 7)
{
    Write-Host "Running on a PowerShell version lower than 7"
    Write-Host "On such versions this script would produce a zip file useless on Linux and Mac due to a" 
    Write-Host "slash/backslash bug in the Compress-Archive cmdlet that was reported to Microsoft"
    Write-Host "over a decade ago."
    Write-Host "Make sure to run this script on PowerShell 7 or higher."
    exit
}

# Try to find the godot environemt variable
$godot = [System.Environment]::GetEnvironmentVariable("Godot", "User")
if (!$godot)
{
    Write-Host "User environent variable 'Godot' not set."
    $godot = Read-Host "Enter full path to godot executable"
    [System.Environment]::SetEnvironmentVariable("Godot", $godot, "User")
}

# Clean the godot viewer directory below io_export_webgo
Remove-Item "./io_export_webgo/godot_viewer" -Recurse -Force

# Clean the godot viewer export/web directory
Remove-Item "./godot_viewer/export" -Recurse -Force

# Create sub-directories export/web
New-Item -Path "./godot_viewer" -name "export" -ItemType "directory"
New-Item -Path "./godot_viewer/export" -name "web" -ItemType "directory"

# Call Godot to build the web export
Start-Process -Wait -FilePath "$godot" -ArgumentList "./godot_viewer/project.godot", "--export-release", "Web", "./export/web/index.html", "--headless"

# Copy the entire godot project (including the just-created web export) below the blender add-on root directory
Copy-Item -Path "./godot_viewer" -Destination "./io_export_webgo/godot_viewer" -Recurse

# Clean-up unnecessary (and zip-destroying) stuff from the copied godot project
Remove-Item "./io_export_webgo/godot_app" -Recurse -Force
Remove-Item "./io_export_webgo/__pycache__" -Recurse -Force
Remove-Item "./io_export_webgo/godot_viewer/.godot" -Recurse -Force

# Zip erverything together
Compress-Archive -Path "./io_export_webgo" -DestinationPath "./io_export_webgo.zip" -Force
