import bpy
import bmesh
from bpy_extras import bmesh_utils


def process_object(context, obj):
    context.view_layer.objects.active = obj
    o_mode = obj.mode

    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)
    uv = bm.loops.layers.uv.active

    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.mark_sharp(clear=True)

    for face in bm.faces:
        face.smooth = True

    islands = bmesh_utils.bmesh_linked_uv_islands(bm, uv)

    edge_island_map = {}

    for island_index, island_faces in enumerate(islands):
        for face in island_faces:
            for edge in face.edges:
                if edge not in edge_island_map:
                    edge_island_map[edge] = set()
                edge_island_map[edge].add(island_index)

    edges_in_multiple_islands = [
        edge for edge, islands in edge_island_map.items() if len(islands) > 1
    ]
    for edge in edges_in_multiple_islands:
        edge.smooth = False

    bmesh.update_edit_mesh(obj.data)
    bm.free()

    bpy.ops.object.mode_set(mode=o_mode)


def main(context):
    o_active = context.active_object
    o_mode = o_active.mode
    o_selected = context.selected_objects.copy()

    for obj in context.view_layer.objects:
        obj.select_set(False)

    for obj in o_selected:
        if obj.type == "MESH":
            process_object(context, obj)

    for obj in context.view_layer.objects:
        obj.select_set(False)
    for obj in o_selected:
        obj.select_set(True)

    context.view_layer.objects.active = o_active
    bpy.ops.object.mode_set(mode=o_mode)



class OBJECT_OT_sharp_edges_by_uv_islands(bpy.types.Operator):
    bl_idname = "object.sharp_edges_by_uv_islands"
    bl_label = "Sharp Edges by UV islands"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(
        OBJECT_OT_sharp_edges_by_uv_islands.bl_idname,
        text=OBJECT_OT_sharp_edges_by_uv_islands.bl_label,
    )


op_keymaps = []


def register_hotkey():
    keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps
    keymap = keymaps.new(name="3D View", space_type="VIEW_3D")
    keymap_item = keymap.keymap_items.new(
        OBJECT_OT_sharp_edges_by_uv_islands.bl_idname,
        type="H",
        value="PRESS",
        shift=True,
        ctrl=True,
        alt=True,
    )
    op_keymaps.append((keymap, keymap_item))


def unregister_hotkey():
    for keymap, keymap_item in op_keymaps:
        keymap.keymap_items.remove(keymap_item)
    op_keymaps.clear()


def register():
    bpy.utils.register_class(OBJECT_OT_sharp_edges_by_uv_islands)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    register_hotkey()


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_sharp_edges_by_uv_islands)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    unregister_hotkey()


if __name__ == "__main__":
    register()
