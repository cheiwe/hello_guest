"""
Vitec (NPC of the Act 1 finale, concept Vitec_Play): the Hunyuan3D mesh (SourceArt/Models/Characters/Vitec/
Vitec_raw.glb) is scaled, turned and textured straight from the concept sheet: front-facing faces get UVs
into the front view of the sheet, back-facing faces into the back view. The material uses the sheet itself
as its colour texture (T_Vitec_Sheet_D).

Stage functions are called from the bottom of the file; rigging and animation live in vitec_rig.py.
"""

import importlib
import math
import os
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

FOLDER = os.path.join(hg.MODELS_DIR, "Characters", "Vitec")
RAW = os.path.join(FOLDER, "Vitec_raw.glb")
# The concept sheet with the figures' colours bled into the background (Scripts/Tools/make_textures.py).
SHEET = os.path.join(hg.PROJECT, "SourceArt", "Textures", "Stylized", "T_Vitec_Sheet_D.png")
HEIGHT = 1.80

# Figure boxes on the 2048 x 2068 sheet (pixels), measured from the image.
SHEET_W, SHEET_H = 2048, 2068
FRONT = (1045, 116, 1502, 1021)
BACK = (1527, 116, 1979, 1020)


def import_raw():
    hg.reset_scene()
    bpy.ops.import_scene.gltf(filepath=RAW)
    obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
    obj.name = "SK_Vitec_Mesh"
    obj.data.name = "SK_Vitec_Mesh"
    return obj


def normalise(obj):
    """1.80 m tall, feet on the floor, facing -Y (like the sheet's front view) for the projection."""
    hg.apply_transforms(obj)
    zs = [v.co.z for v in obj.data.vertices]
    scale = HEIGHT / (max(zs) - min(zs))
    obj.data.transform(Matrix.Scale(scale, 4))
    zs = [v.co.z for v in obj.data.vertices]
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    obj.data.transform(Matrix.Translation((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs))))
    obj.data.update()


def project_sheet(obj):
    """UVs into the concept sheet: front view for faces towards -Y, back view for the others."""
    mesh = obj.data
    if mesh.uv_layers:
        for layer in list(mesh.uv_layers):
            mesh.uv_layers.remove(layer)
    uv = mesh.uv_layers.new(name="UVMap").data

    xs = [v.co.x for v in mesh.vertices]
    half_width = max(abs(min(xs)), abs(max(xs)))
    top = max(v.co.z for v in mesh.vertices)

    fx0, fy0, fx1, fy1 = FRONT
    bx0, by0, bx1, by1 = BACK
    px_per_m = (fy1 - fy0) / top
    shoulder = 0.22
    # Arms of the generated mesh spread wider than on the sheet: squeeze beyond the shoulders so the
    # hands land on the drawn hands.
    arm_k = ((fx1 - fx0) / 2 - shoulder * px_per_m) / ((half_width - shoulder) * px_per_m)

    def squeeze(x):
        a = abs(x)
        m = a if a < shoulder else shoulder + (a - shoulder) * arm_k
        return math.copysign(m * px_per_m, x)

    for poly in mesh.polygons:
        front = poly.normal.y < 0 or (abs(poly.normal.y) < 0.2 and poly.center.y < 0)
        # Faces turned sideways would sample the drawn outline at the silhouette edge (stripes): pull
        # their samples inwards, up to 12 % of the distance from the centre line.
        inset = 1.0 - 0.12 * abs(poly.normal.x)
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            py = (top - co.z) * px_per_m
            if front:
                px = (fx0 + fx1) / 2 + squeeze(co.x) * inset
                py += fy0
            else:
                # Seen from behind the character's right side is on the right of the drawing.
                px = (bx0 + bx1) / 2 - squeeze(co.x) * inset * (bx1 - bx0) / (fx1 - fx0)
                py = by0 + (top - co.z) * (by1 - by0) / top
            uv[li].uv = (px / SHEET_W, 1.0 - py / SHEET_H)


def sheet_material(obj):
    """M_Vitec with the sheet as an image texture (Blender preview; Unreal uses MI_Vitec)."""
    mat = bpy.data.materials.get("M_Vitec") or bpy.data.materials.new("M_Vitec")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None) or nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(SHEET, check_existing=True)
    tex.interpolation = "Linear"
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.75
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def face_forward(obj):
    """Turn to face +X (Unreal's forward; X is not mirrored on export)."""
    obj.data.transform(Matrix.Rotation(math.radians(90), 4, "Z"))
    obj.data.update()


def build_textured():
    obj = import_raw()
    normalise(obj)
    project_sheet(obj)
    sheet_material(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    face_forward(obj)
    hg.save_blend(os.path.join(FOLDER, "Vitec_Textured.blend"))
    print("Vitec textured:", tuple(round(d, 3) for d in obj.dimensions), len(obj.data.polygons), "faces")
    return obj


if __name__ == "__main__" or True:
    build_textured()
