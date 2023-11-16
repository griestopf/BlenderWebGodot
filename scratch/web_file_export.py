import bpy
import os

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import Operator, AddonPreferences

the_unique_name_of_the_addon = "io_export_webgo"


bl_info = {
    "name": "Export to Web (powered by Godot)",
    "author": "Christoph Müller",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "File > Export > Web",
    "description": "Exports a 3D scene that can be viewed in Web Browsers using the Godot Open-Source Game-Engine",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

#######################################################################################################


#get the folder path for the .py file containing this function
def get_path():
    return os.path.dirname(os.path.realpath(__file__))


def do_export_web(context, filepath, use_some_setting):
    print("running do_export_web...")
    preferences = context.preferences
    addon_prefs = preferences.addons[the_unique_name_of_the_addon].preferences

    # where are we?
    print("os.getcwd():  ", os.getcwd())
    print("os.path.dirname(os.path.realpath(__file__)) ", os.path.dirname(os.path.realpath(__file__)));

    bpy.ops.export_scene.gltf(filepath=filepath)

    #f = open(filepath, 'w', encoding='utf-8')
    #f.write("Hello World %s" % use_some_setting)
    #f.close()

    return {'FINISHED'}


#######################################################################################################

class ExportWebPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = the_unique_name_of_the_addon

    filepath: StringProperty(
        name="Godot Executable",
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
        layout.label(text="This is a preferences view for our add-on")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")


#######################################################################################################

class ExportWeb(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_scene.web"  # important since its how bpy.ops.export_scene.web is constructed
    bl_label = "Export Web"
    bl_options = {'UNDO', 'PRESET'}

    # ExportHelper mix-in class uses this.
    filename_ext = ".html"

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


#######################################################################################################


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportWeb.bl_idname, text="Web Exporter")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportWeb)
    bpy.utils.register_class(ExportWebPreferences)    
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportWeb)
    bpy.utils.unregister_class(ExportWebPreferences)    
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_scene.web('INVOKE_DEFAULT')
