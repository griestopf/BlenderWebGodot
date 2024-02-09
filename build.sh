#!/bin/bash

# Try to find the godot environemt variable
if [ -z "${GODOT}" ]; then
    echo "GODOT environment variable is not set."
    read -p "Enter path to the Godot executable: " godot
    export GODOT=$godot
else
    echo "Using Godot at ${GODOT}"
    godot="${GODOT}"
fi

# Clean the godot viewer directory below io_export_webgo
# PS> Remove-Item "./io_export_webgo/godot_viewer" -Recurse -Force
rm -rf "./io_export_webgo/godot_viewer"

# Clean the godot viewer export/web directory
# Remove-Item "./godot_viewer/export" -Recurse -Force
rm -rf "./godot_viewer/export"

# Create sub-directories export/web
# PS> New-Item -Path "./godot_viewer" -name "export" -ItemType "directory"
# PS> New-Item -Path "./godot_viewer/export" -name "web" -ItemType "directory"
cd "./godot_viewer"
mkdir "export"
cd "./export"
mkdir "web"
cd ..
cd ..


# Call Godot to build the web export
# PS> Start-Process -Wait -FilePath "$godot" -ArgumentList "./godot_viewer/project.godot", "--export-release", "Web", "./export/web/index.html", "--headless"
$godot ./godot_viewer/project.godot --export-release Web ./export/web/index.html --headless

# Copy the entire godot project (including the just-created web export) below the blender add-on root directory
# PS> Copy-Item -Path "./godot_viewer" -Destination "./io_export_webgo/godot_viewer" -Recurse
cp -r "./godot_viewer" "./io_export_webgo/godot_viewer"

# Clean-up unnecessary (and zip-destroying) stuff from the copied godot project
# PS> Remove-Item "./io_export_webgo/godot_app" -Recurse -Force
# PS> Remove-Item "./io_export_webgo/__pycache__" -Recurse -Force
# PS> Remove-Item "./io_export_webgo/godot_viewer/.godot" -Recurse -Force
rm -rf "./io_export_webgo/godot_app"
rm -rf "./io_export_webgo/__pycache__"
rm -rf "./io_export_webgo/godot_viewer/.godot"

# Zip erverything together
# PS> Compress-Archive -Path "./io_export_webgo" -DestinationPath "./io_export_webgo.zip" -Force
zip -r "./io_export_webgo.zip" "./io_export_webgo"
