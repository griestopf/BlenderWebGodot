Remove-Item "./io_export_webgo/godot_app" -Recurse -Force
Remove-Item "./io_export_webgo/__pycache__" -Recurse -Force
Remove-Item "./io_export_webgo/godot_viewer/.godot" -Recurse -Force
Compress-Archive -Path "./io_export_webgo" -DestinationPath "./io_export_webgo.zip" -Force
