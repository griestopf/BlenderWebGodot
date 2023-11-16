import subprocess

godot_args = [
        r"C:\Users\chris\Documents\_DEV\Godot\v4.1.3\Godot_v4.1.3-stable_win64_console.exe",
        "project.godot",
        "--export-release",
        "Web",
        r"Export\Web\index.html",
        "--headless"
    ]
subprocess.run(godot_args)
