#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

from mathutils import *
from bpy.props import *
import bpy
import bmesh
import os
import math
import sys

# Version history
# 1.0.0 - 2022-02-06: Original version.
# 1.0.1 - 2022-02-07: Removed Insert Helicopter Hair Guide button from N panel.
# 1.0.2 - 2022-02-07: Renamed "Place Helicopter Hair" to "Automatically Comb Helicopter Hair".
# 1.0.3 - 2022-03-03: Modified the add-on to work better with recombing hair after it's already been automatically combed; hairs aren't
#                     automatically deselected when you rotate the camera. However, there is still a class behind the scenes --
#                     rhhc.rotate_add_plus_deselect -- that gets called by a Blender keyboard shortcut. (The AutoHotKey script will call
#                     that keyboard shortcut.) Also improved the AutoIt script so it can be paused (no more runaway AutoIt script!)
# 1.0.4 - 2022-03-06: Renamed "Automatically Comb Helicopter Hair" to "Auto Comb Helicopter Hair".
#                     Added Camera Z location control (always wanted it, found that I was really needing it).
#                     Changed the label for Camera Z rotation so it shows the actual input box -- you can change/set the value in there directly.
#                     Added the feature "Comb Sel Hair Right".
#                     Added the feature "Comb Sel Hair Down".
# 1.0.5 = 2022-03-07: Realized I needed combing left and up as well. Renamed add-on to "Comb Utilities" since this add-on has evolved to be much
#                     more than just the hair helicopter technique. Re-arranged the panel, putting hte most useful options at the top.
#                     Added a "Strokes" option so it doesn't always do two combing strokes (sometimes one is plenty). Combined all of the
#                     AutoIt scripts into one script where you feed it the command line params for direction and strokes.
# 1.0.6 - 2022-08-07: Misc formatting cleanup before uploading to GitHub.

###############################################################################
SCRIPT_NAME = 'comb_utilities'

# This Windows-only Blender add-on has hair-related functions for automatically combing hair.
# You need to set up several keyboard shortcuts to properly use this:
#
#      * 3D View → 3D View (Global) keyboard shortcut so that Shift Ctrl ] gets assigned to "rhhc.rotate_add_plus_deselect". (This is required for the Auto Comb Helicopter Hair script.)
#      * 3D View → 3D View (Global) keyboard shortcut so that Shift Ctrl [ gets assigned to "rhhc.done_combing". (This is required for the Comb Selected Hair Down script -- it's the only way that we know whether we need to toggle off the X-Ray.)
#      * 3D View → 3D View (Global) keyboard shortcut so that Alt Numpad 8 gets assigned to "rhhc.comb_selected_hair_up". (This makes it easier for the user to repeatedly comb hair downward.)
#      * 3D View → 3D View (Global) keyboard shortcut so that Alt Numpad 2 gets assigned to "rhhc.comb_selected_hair_down". (This makes it easier for the user to repeatedly comb hair downward.)
#      * 3D View → 3D View (Global) keyboard shortcut so that Alt Numpad 4 gets assigned to "rhhc.comb_selected_hair_left". (This makes it easier for the user to repeatedly comb hair to the right.)
#      * 3D View → 3D View (Global) keyboard shortcut so that Alt Numpad 6 gets assigned to "rhhc.comb_selected_hair_right". (This makes it easier for the user to repeatedly comb hair to the right.)
#
###############################################################################

bl_info = {
    "name": "Comb Utilities",
    "author": "Jeff Boller",
    "version": (1, 0, 6),
    "blender": (2, 93, 0),
    "location": "View3D > Properties > Hair",
    "description": 'This Windows-only Blender add-on has hair-related functions for automatically combing hair.',
    "wiki_url": "https://github.com/sundriftproductions/blenderaddon-comb-utilities/wiki",
    "tracker_url": "https://github.com/sundriftproductions/blenderaddon-comb-utilities",
    "category": "3D View"}

class HelicopterHairPreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = __module__
    turn_off_x_ray_when_done_combing: bpy.props.BoolProperty(default=True)

    enum_strokes: bpy.props.EnumProperty(
        name="enum_strokes",
        description="How many combing strokes we should perform",
        items=[
            ('1', '1', '1'),
            ('2', '2', '2'),
            ('3', '3', '3'),
        ], default='2')

    def draw(self, context):
        self.layout.label(text="Current values")

class COMBUTILITIES_PT_AutoCombHelicopterHair(bpy.types.Operator):
    bl_idname = "rhhc.auto_comb_helicopter_hair"
    bl_label = "Auto Comb Helicopter Hair"
    bl_description = "Combs the individual hair strands to make helicopter hair"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        script = os.path.dirname(os.path.realpath(__file__)) + '/auto_comb_helicopter_hair.au3'
        script = script.replace("\\", "/")
        os.spawnl(os.P_NOWAIT, "C:\Program Files (x86)\AutoIt3\AutoIt3.exe", 'autoit.exe', script)
        return {"FINISHED"}

class COMBUTILITIES_PT_CombSelectedHairLeft(bpy.types.Operator):
    bl_idname = "rhhc.comb_selected_hair_left"
    bl_label = ""
    bl_description = "Combs the selected hair strands to the left"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # If we only have some of a hair selected, select the whole thing.
        bpy.ops.particle.select_linked()

        # Now call the script.
        script = os.path.dirname(os.path.realpath(__file__)) + '/comb_selected_hair.au3 L ' + bpy.context.preferences.addons['comb_utilities'].preferences.enum_strokes
        script = script.replace("\\", "/")
        os.spawnl(os.P_NOWAIT, "C:\Program Files (x86)\AutoIt3\AutoIt3.exe", 'autoit.exe', script)
        return {"FINISHED"}

class COMBUTILITIES_PT_CombSelectedHairRight(bpy.types.Operator):
    bl_idname = "rhhc.comb_selected_hair_right"
    bl_label = ""
    bl_description = "Combs the selected hair strands to the right"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # If we only have some of a hair selected, select the whole thing.
        bpy.ops.particle.select_linked()

        # Now call the script.
        script = os.path.dirname(os.path.realpath(__file__)) + '/comb_selected_hair.au3 R ' + bpy.context.preferences.addons['comb_utilities'].preferences.enum_strokes
        script = script.replace("\\", "/")
        os.spawnl(os.P_NOWAIT, "C:\Program Files (x86)\AutoIt3\AutoIt3.exe", 'autoit.exe', script)
        return {"FINISHED"}

class COMBUTILITIES_PT_CombSelectedHairDown(bpy.types.Operator):
    bl_idname = "rhhc.comb_selected_hair_down"
    bl_label = ""
    bl_description = "Combs the selected hair strands down"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.preferences.addons['comb_utilities'].preferences.turn_off_x_ray_when_done_combing = False

        views3d = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D']
        for a in views3d:
            shading = a.spaces.active.shading
            if not shading.show_xray:
                shading.show_xray = True
                bpy.context.preferences.addons['comb_utilities'].preferences.turn_off_x_ray_when_done_combing = True # This won't be 100% accurate if we have multiple 3D Viewport windows with different x-ray states, but this is good enough.

        # Now call the script.
        script = os.path.dirname(os.path.realpath(__file__)) + '/comb_selected_hair.au3 D ' + bpy.context.preferences.addons['comb_utilities'].preferences.enum_strokes
        script = script.replace("\\",
                          "/")  # Replace all of the backslashes in our path with forward slashes. This will still work on Windows if you don't do this, but this is just to be consistent.
        os.spawnl(os.P_NOWAIT, "C:\Program Files (x86)\AutoIt3\AutoIt3.exe", 'autoit.exe', script)

        return {"FINISHED"}

class COMBUTILITIES_PT_CombSelectedHairUp(bpy.types.Operator):
    bl_idname = "rhhc.comb_selected_hair_up"
    bl_label = ""
    bl_description = "Combs the selected hair strands up"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.preferences.addons['comb_utilities'].preferences.turn_off_x_ray_when_done_combing = False

        views3d = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D']
        for a in views3d:
            shading = a.spaces.active.shading
            if not shading.show_xray:
                shading.show_xray = True
                bpy.context.preferences.addons['comb_utilities'].preferences.turn_off_x_ray_when_done_combing = True # This won't be 100% accurate if we have multiple 3D Viewport windows with different x-ray states, but this is good enough.

        # Now call the script.
        script = os.path.dirname(os.path.realpath(__file__)) + '/comb_selected_hair.au3 U ' + bpy.context.preferences.addons['comb_utilities'].preferences.enum_strokes
        script = script.replace("\\",
                          "/")  # Replace all of the backslashes in our path with forward slashes. This will still work on Windows if you don't do this, but this is just to be consistent.
        os.spawnl(os.P_NOWAIT, "C:\Program Files (x86)\AutoIt3\AutoIt3.exe", 'autoit.exe', script)

        return {"FINISHED"}

class COMBUTILITIES_PT_MoveCameraToCursorXY(bpy.types.Operator):
    bl_idname = "rhhc.move_camera_to_cursor_xy"
    bl_label = "Move Camera to 3D Cursor XY"

    def execute(self, context):
        bpy.context.scene.camera.location[0] = bpy.context.scene.cursor.location[0];
        bpy.context.scene.camera.location[1] = bpy.context.scene.cursor.location[1];
        bpy.context.scene.camera.rotation_euler[0] = math.radians(180);
        bpy.context.scene.camera.rotation_euler[1] = math.radians(180);
        bpy.context.scene.camera.rotation_euler[2] = math.radians(180);
        return {'FINISHED'}

class COMBUTILITIES_PT_RotateAdd(bpy.types.Operator):
    bl_idname = "rhhc.rotate_add"
    bl_label = "+"

    def execute(self, context):
        bpy.context.scene.camera.rotation_euler[2] += math.radians(1);
        return {'FINISHED'}

# This class isn't technically used in the add-on. HOWEVER...it's called via keyboard shortcut by the comb_selected_hair_down.au3 script when it's done running.
class COMBUTILITIES_PT_DoneCombing(bpy.types.Operator):
    bl_idname = "rhhc.done_combing"
    bl_label = "rhhc.done_combing"

    def execute(self, context):
        try:
            if bpy.context.preferences.addons['comb_utilities'].preferences.turn_off_x_ray_when_done_combing:
                views3d = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D']
                for a in views3d:
                    shading = a.spaces.active.shading
                    shading.show_xray = False
        except:
            pass

        self.report({'INFO'}, 'Done combing!')
        return {'FINISHED'}

# This class isn't technically used in the add-on. HOWEVER...it's called via keyboard shortcut by the auto_comb_helicopter_hair.au3 script.
# The only difference between this call and the COMBUTILITIES_PT_RotateAdd call is that this deselects the hair after we do a rotate. That's something
# which is very useful for the AutoIt script but absolutely not what we want if we want to manually comb helicopter hair.
class COMBUTILITIES_PT_RotateAddPlusDeselect(bpy.types.Operator):
    bl_idname = "rhhc.rotate_add_plus_deselect"
    bl_label = "rhhc.rotate_add_plus_deselect"

    def execute(self, context):
        bpy.context.scene.camera.rotation_euler[2] += math.radians(1);
        if bpy.context.active_object.mode == 'PARTICLE_EDIT':
            bpy.ops.particle.select_all(action='DESELECT')
        return {'FINISHED'}

class COMBUTILITIES_PT_RotateSubtract(bpy.types.Operator):
    bl_idname = "rhhc.rotate_subtract"
    bl_label = "-"

    def execute(self, context):
        bpy.context.scene.camera.rotation_euler[2] -= math.radians(1);
        return {'FINISHED'}

class COMBUTILITIES_PT_Main(bpy.types.Panel):
    bl_idname = "COMBUTILITIES_PT_Main"
    bl_label = "Comb Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hair"

    def draw(self, context):
        if bpy.context.scene.camera != None:
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text="Comb Selected Hair")
            row = box.row(align=True)
            col = row.column()
            col.label(text = " ")
            col = row.column()
            col.label(text = " ")
            col = row.column()
            col.operator("rhhc.comb_selected_hair_up", icon='TRIA_UP')
            col = row.column()
            col.label(text=" ")
            col = row.column()
            col.label(text = " ")

            row = box.row(align=True)
            col = row.column()
            col.label(text = " ")
            col = row.column()
            col.operator("rhhc.comb_selected_hair_left", icon='TRIA_LEFT')
            col = row.column()
            col.label(text=" ")
            col = row.column()
            col.operator("rhhc.comb_selected_hair_right", icon='TRIA_RIGHT')
            col = row.column()
            col.label(text = " ")

            row = box.row(align=True)
            col = row.column()
            col.label(text=" ")
            col = row.column()
            col.label(text = " ")
            col = row.column()
            col.operator("rhhc.comb_selected_hair_down", icon='TRIA_DOWN')
            col = row.column()
            col.label(text=" ")
            col = row.column()
            col.label(text = " ")

            row = box.row(align=True)
            row.label(text="Strokes: ")
            row.prop(bpy.context.preferences.addons['comb_utilities'].preferences, "enum_strokes", expand=True)

            box.enabled = (bpy.context.active_object.mode == 'PARTICLE_EDIT')

            row = self.layout.row(align=True)

            box = self.layout.box()
            row = box.row(align=True)
            row.column().operator("rhhc.move_camera_to_cursor_xy", icon='VIEW_CAMERA')

            row = box.row()
            row.column().prop(bpy.context.scene.camera, "location", index=2, text="'" + bpy.context.scene.camera.name + "' Z Location")

            row = self.layout.row(align=True)

            box = self.layout.box()
            row = box.row(align=True)
            row.label(text="Rotate '" + bpy.context.scene.camera.name + "' Z:")
            row.operator("rhhc.rotate_subtract")
            row.operator("rhhc.rotate_add")

            row = box.row(align=True)
            row.column().prop(bpy.context.scene.camera, "rotation_euler", index=2, text="'" + bpy.context.scene.camera.name + "' Z Rotation")

            row = self.layout.row(align=True)

            row = self.layout.row(align=True)
            row.operator("rhhc.auto_comb_helicopter_hair", icon='PARTICLE_POINT')
            row.enabled = (bpy.context.active_object.mode == 'PARTICLE_EDIT')
        else:
            box = self.layout.box()
            row = box.row()
            row.scale_y = 0.6
            row.label(text="There is no Camera object in this scene.")

def register():
    bpy.utils.register_class(HelicopterHairPreferencesPanel)
    bpy.utils.register_class(COMBUTILITIES_PT_AutoCombHelicopterHair)
    bpy.utils.register_class(COMBUTILITIES_PT_CombSelectedHairLeft)
    bpy.utils.register_class(COMBUTILITIES_PT_CombSelectedHairRight)
    bpy.utils.register_class(COMBUTILITIES_PT_CombSelectedHairDown)
    bpy.utils.register_class(COMBUTILITIES_PT_CombSelectedHairUp)
    bpy.utils.register_class(COMBUTILITIES_PT_Main)
    bpy.utils.register_class(COMBUTILITIES_PT_MoveCameraToCursorXY)
    bpy.utils.register_class(COMBUTILITIES_PT_RotateAdd)
    bpy.utils.register_class(COMBUTILITIES_PT_RotateAddPlusDeselect)
    bpy.utils.register_class(COMBUTILITIES_PT_DoneCombing)
    bpy.utils.register_class(COMBUTILITIES_PT_RotateSubtract)

def unregister():
    bpy.utils.unregister_class(HelicopterHairPreferencesPanel)
    bpy.utils.unregister_class(COMBUTILITIES_PT_AutoCombHelicopterHair)
    bpy.utils.unregister_class(COMBUTILITIES_PT_CombSelectedHairLeft)
    bpy.utils.unregister_class(COMBUTILITIES_PT_CombSelectedHairRight)
    bpy.utils.unregister_class(COMBUTILITIES_PT_CombSelectedHairDown)
    bpy.utils.unregister_class(COMBUTILITIES_PT_CombSelectedHairUp)
    bpy.utils.unregister_class(COMBUTILITIES_PT_Main)
    bpy.utils.unregister_class(COMBUTILITIES_PT_MoveCameraToCursorXY)
    bpy.utils.unregister_class(COMBUTILITIES_PT_RotateAdd)
    bpy.utils.unregister_class(COMBUTILITIES_PT_RotateAddPlusDeselect)
    bpy.utils.unregister_class(COMBUTILITIES_PT_DoneCombing)
    bpy.utils.unregister_class(COMBUTILITIES_PT_RotateSubtract)

if __name__ == "__main__":
    register()
