# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
import os
import stat
import subprocess
import platform
import shutil
from urllib.request import urlretrieve

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import Operator, AddonPreferences

bl_info = {
    "name": "Export to Web (powered by Godot)",
    "author": "Christoph Müller",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "File > Export > Web",
    "description": "Exports a 3D scene that can be viewed in Web Browsers using the Godot Open-Source Game-Engine",
    "warning": "",
    "doc_url": "https://github.com/griestopf/BlenderWebGodot",
    "category": "Import-Export",
}

the_unique_name_of_the_addon   = "io_export_webgo"
the_readable_name_of_the_addon = "Export to Web (powered by Godot)"

the_unique_name_of_the_download_button = "io_export_webgo.download_godot"
the_required_godot_version = ""



#######################################################################################################


#get the folder path for the .py file containing this function
def get_path():
    return os.path.dirname(os.path.realpath(__file__))


def draw_godot_download_settings(parent):
    layout = parent.layout
    pcoll = preview_collections["main"]
    my_icon = pcoll["my_icon"]        
    layout.operator(the_unique_name_of_the_download_button, icon_value=my_icon.icon_id)
    layout.prop(parent, "godot_path")

def report_error(header: str, msg: str):
    ShowMessageBox(msg, header, 'ERROR')
    print(header + ": " + msg)
    
def do_export_web(context, filepath, use_some_setting):
    print("running do_export_web...")
    if not is_godot4_present(context):
        # Godot is not downloaded. Open the Blender Add-on preferences with this
        # Add-On's settings expanded.
        bpy.ops.screen.userpref_show()
        bpy.context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = the_readable_name_of_the_addon
        bpy.data.window_managers["WinMan"].addon_support = {'COMMUNITY'}
        bpy.ops.preferences.addon_show(module=the_unique_name_of_the_addon)
        report_error("ERROR Godot not present", "Godot 4 or higher is not available. Try 'Download Godot' or set the 'Godot App' path in Edit>Preferences>Add-Ons>'Export to Web (powered by Godot)'!")
        return {'CANCELLED'}

    # assemble target path
    p_target_dir = filepath[:filepath.rindex(".")]
    p_target_pck = os.path.join(p_target_dir, "index.pck")
    p_target_servepy = os.path.join(p_target_dir, "serve.py")
    p_target_servebat = "unknown"
    p_servebat_contents = ""
    match platform.system():
        case "Windows":
            p_target_servebat = p_target_dir + ".bat"
            # no shebang on windows
        case "Linux":
            p_target_servebat = p_target_dir + ".bash"
            p_servebat_contents = "#!/bin/bash\n" # should do on most *nixes
        case "Darwin":
            p_target_servebat = p_target_dir + ".command"
            p_servebat_contents = "#!/bin/bash\n" # will do on MacOS
    if p_target_servebat == "unknown":
        report_error(header = "ERROR Exporting to Web", msg = "Unknown platform '" + platform.system() +"'")
        return {'CANCELLED'}

    p_blender_exe = bpy.app.binary_path
    p_servebat_contents += '"' + p_blender_exe + '" --background --python "' + p_target_servepy + '" -- --root "' + p_target_dir + '" --port 55544'
    
    # assemble paths relative to this addon
    preferences = context.preferences
    addon_prefs = preferences.addons[the_unique_name_of_the_addon].preferences
    p_godot_app = addon_prefs.godot_path
   
    p_addon = get_path()
    p_glb_scene = os.path.join(p_addon, "godot_viewer", "model", "model.glb")
    p_godot_project = os.path.join(p_addon, "godot_viewer", "project.godot")
    p_web_export_dir = os.path.join(p_addon, "godot_viewer", "export", "web")
    p_web_export_pck = os.path.join(p_web_export_dir, "index.pck")
    p_src_servepy = os.path.join(p_addon, "serve.py")

    # where are we?
    print("p_addon          ", p_addon          )
    print("p_glb_scene      ", p_glb_scene      )
    print("p_godot_console  ", p_godot_app      )
    print("p_godot_project  ", p_godot_project  )
    print("p_web_export_dir ", p_web_export_dir )
    
    print("p_target_dir     ", p_target_dir)
    print("p_target_pck     ", p_target_pck)

    # Remove anything exisiting with the name
    # e.g. a directory with the given name
    if os.path.isdir(p_target_dir):
        try:
            shutil.rmtree(p_target_dir)
        except:
            report_error(header = "ERROR Exporting to Web", msg = "Could not remove existing directory'" + p_target_dir +"'")
            return {'CANCELLED'}
    # or a file with the exact name
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except:
            report_error(header = "ERROR Exporting to Web", msg = "Could not remove existing file '" + filepath +"'")
    # or the starter batch file
    if os.path.isfile(p_target_servebat):
        try:
            os.remove(p_target_servebat)
        except:
            report_error(header = "ERROR Exporting to Web", msg = "Could not remove existing file '" + p_target_servebat +"'")
    

    # Check if local dir 'p_target_dir' exists and create if not
    # if not os.path.isdir(p_target_dir):
    #     try:
    #         os.makedirs(p_target_dir)
    #     except OSError as exc:
    #         report_error(header = "ERROR Exporting to Web", msg = "Cannot create directory '" + p_target_dir +"'")
    #         return {'CANCELLED'}

    # Copy the original viewer's web export to the target directory
    try:
        shutil.copytree(p_web_export_dir, p_target_dir)
    except:
        report_error(header = "ERROR Exporting to Web", msg = "Cannot copy contents from '" + p_web_export_dir +"' to '" + p_target_dir +"'")
        return {'CANCELLED'}

    # Copy the serve.py script necessary to locally display the web contents
    try:
        shutil.copy2(p_src_servepy, p_target_dir)
    except:
        report_error(header = "ERROR Exporting to Web", msg = "Cannot copy '" + p_src_servepy +"' to '" + p_target_dir +"'")
        return {'CANCELLED'}
    
    # Create the batch file to call serve.py and make the batch file executable
    try:
        f = open(p_target_servebat, "w")
        f.write(p_servebat_contents)
        f.close()
        st = os.stat(p_target_servebat)
        os.chmod(p_target_servebat, st.st_mode | stat.S_IXGRP | stat.S_IXUSR | stat.S_IXOTH)
    except:
        report_error(header = "ERROR Exporting to Web", msg = "Cannot create '" + p_target_servebat + "'")
        return {'CANCELLED'}

    # Export blender contents to gltf and run godot to overwrite the .pck web contents
    bpy.ops.export_scene.gltf(filepath=p_glb_scene)
    godot_args = [
        p_godot_app,
        p_godot_project,
        "--export-pack",
        "Web",
        p_target_pck,
        "--headless"
    ]
    print(godot_args)
    subprocess.run(godot_args)

    #f = open(filepath, 'w', encoding='utf-8')
    #f.write("Hello World %s" % use_some_setting)
    #f.close()

    return {'FINISHED'}

def is_godot4_present(context):
    '''Check if the godot app file exists. If so, call it with the --version parameter and check if it outputs "4" as the first digit.'''
    preferences = context.preferences
    addon_prefs = preferences.addons[the_unique_name_of_the_addon].preferences
    p_godot_app = addon_prefs.godot_path
    if not p_godot_app:
        return False
    if not os.path.isfile(p_godot_app):
        return False
    godot_args = [
        p_godot_app,
        "--version"
    ]
    result = subprocess.run(godot_args, capture_output = True, text = True)
    if len(result.stdout) < 2 or int(result.stdout[0]) < 4:
        return False
    return True



#######################################################################################################

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)



#######################################################################################################

class DownloadGodotOperator(bpy.types.Operator):
    """Download the Godot game engine and store it in a local directory. This will set the 'Godot App' path setting below to the downloaded Godot version. Godot is called during Web Export to convert the Blender 3D content into a format displayable in web browsers. If you already have Godot without MONO installed on your machine you do not need to download Godot. Instead, set the 'Godot App' path to your existing Godot without MONO installation"""
    bl_idname = the_unique_name_of_the_download_button
    bl_label = "Download Godot"

    def execute(self, context):
        # Platform-specific info.
        # Windows:
        #    platform.system(): "Windows"
        #    Download-URL:      https://github.com/godotengine/godot-builds/releases/download/4.1.3-stable/Godot_v4.1.3-stable_win64.exe.zip
        #    Executable:        Godot_v4.1.3-stable_win64.exe   OR   Godot_v4.1.3-stable_win64_console.exe
        # Linux:
        #    platform.system(): "Linux"
        #    Download-URL:      https://github.com/godotengine/godot-builds/releases/download/4.1.3-stable/Godot_v4.1.3-stable_linux.x86_64.zip
        #    Executable:        Godot_v4.1.3-stable_linux.x86_64
        # MacOS:
        #    platform.system(): "Darwin"
        #    Download-URL:      https://github.com/godotengine/godot-builds/releases/download/4.1.3-stable/Godot_v4.1.3-stable_macos.universal.zip
        #    Executable:        Godot.app (Folder)   OR   Godot.app/Contents/MacOS/Godot (Executable)
        godot_version = "4.2.1-stable"
        godot_platform = "unknown"
        godot_app = "unknown"
        match platform.system():
            case "Windows":
                godot_platform = "win64.exe"
                godot_app = "Godot_v" + godot_version + "_" + godot_platform
            case "Linux":
                godot_platform = "linux.x86_64"
                godot_app = "Godot_v" + godot_version + "_" + godot_platform
            case "Darwin":
                godot_platform = "macos.universal"
                godot_app = "Godot.app"
        if godot_platform == "unknown":
            report_error(header = "ERROR Downloading Godot", msg = "Unknown platform '" + platform.system() +"'")
            return {'CANCELLED'}

        # Construct necessery paths
        file_name = "Godot_v" + godot_version + "_" + godot_platform + ".zip"
        download_url = "https://github.com/godotengine/godot-builds/releases/download/" + godot_version + "/" + file_name
        p_addon = get_path()
        p_local_dir_path = os.path.join(p_addon, "godot_app")
        p_local_zip_path = os.path.join(p_local_dir_path, file_name)
        p_local_app_path = os.path.join(p_local_dir_path, godot_app)
        
        # Check if local dir 'godot_app' exists and create if not
        if not os.path.isdir(p_local_dir_path):
            try:
                os.makedirs(p_local_dir_path)
            except:
                report_error(header = "ERROR Downloading Godot", msg = "Cannot create directory'" + p_local_dir_path +"'")
                return {'CANCELLED'}

        # Download Godot from official GitHub repo
        print("Downloading Godot from '", download_url, "' to '", p_local_zip_path, "'")
        try:
            urlretrieve(download_url, p_local_zip_path)
        except:
            report_error(header = "ERROR Downloading Godot", msg = "Cannot download Godot from '" + download_url +"'")
            return {'CANCELLED'}

        # Unzip the download
        try:
            shutil.unpack_archive(p_local_zip_path, p_local_dir_path)
        except:
            report_error(header = "ERROR Downloading Godot", msg = "Cannot unzip downloaded Godot at '" + p_local_zip_path +"'")
            return {'CANCELLED'}

        # Delete the zip file
        try:
            os.remove(p_local_zip_path)
        except:
            report_error(header = "Warning", msg = "Could not remove Godot zip file after extracting it '" + p_local_zip_path +"'")

        # Set the path to downloaded Godot in this Add-On's preferences
        preferences = context.preferences
        addon_prefs = preferences.addons[the_unique_name_of_the_addon].preferences
        addon_prefs.godot_path = p_local_app_path

        return {'FINISHED'}


class ExportWebPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = the_unique_name_of_the_addon

    godot_path: StringProperty(
        name="Godot App",
        description="Valid file path to the local Godot 4 Application/Executable. If you already downloaded Godot 4 without MONO, specify your local installation here. Ohterwise, use the 'Download Godot' button above to download an appropriate Godot version and set the path automatically",
        subtype='FILE_PATH',
    )
    number: IntProperty(
        name="Example Number",
        default=4,
    )
    boolean: BoolProperty(
        name="Example Boolean",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        draw_godot_download_settings(self)

        #layout.label(text="Download Godot v4 or higher (WIHTOUT mono)")
        #layout.label(text="from godotengine.org/download,")
        #layout.label(text="extract it to a local folder and")
        #layout.label(text="specify the file path to it below.")
     
        # pcoll = preview_collections["main"]
        # my_icon = pcoll["my_icon"]        
        # layout.operator(the_unique_name_of_the_download_button, icon_value=my_icon.icon_id)
        # layout.prop(self, "godot_path")

        #layout.prop(self, "number")
        #layout.prop(self, "boolean")

# See https://blenderartists.org/t/best-practice-for-addon-key-bindings-own-preferences-or-blenders/1416828
# to add a button as an operator


#######################################################################################################

class ExportWeb(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_scene.web"  # important since its how bpy.ops.export_scene.web is constructed
    bl_label = "Export Web"
    bl_options = {'UNDO', 'PRESET'}

    # ExportHelper mix-in class uses this.
    filename_ext = ".html"

    godot_present = False

    godot_path: StringProperty(
        name="Godot App",
        subtype='FILE_PATH',
    )

    filter_glob: StringProperty(
        default="*.html",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return do_export_web(context, self.filepath, self.use_setting)
    
    def invoke(self, context, event):
        self.godot_present = is_godot4_present(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def draw(self, context):
        layout = self.layout

        if not self.godot_present:
            layout.label(text="Godot 4 not present", icon='ERROR')
            return

        # preferences = context.preferences
        # addon_prefs = preferences.addons[the_unique_name_of_the_addon].preferences
        # self.godot_path = addon_prefs.godot_path
        layout.label(text="Godot 4 is present", icon='CHECKMARK')



#######################################################################################################


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportWeb.bl_idname, text="Web Exporter")

# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    # Custom icon registration taken from https://docs.blender.org/api/4.0/bpy.utils.previews.html
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load("my_icon", os.path.join(my_icons_dir, "godot_icon.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    bpy.utils.register_class(DownloadGodotOperator)
    bpy.utils.register_class(ExportWeb)
    bpy.utils.register_class(ExportWebPreferences)    
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    # Custom icon deregistration
    for pcoll in preview_collections.values():
         bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(DownloadGodotOperator)
    bpy.utils.unregister_class(ExportWeb)
    bpy.utils.unregister_class(ExportWebPreferences)    
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_scene.web('INVOKE_DEFAULT')
