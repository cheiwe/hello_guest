"""
Review scene for the hallway kit: a short corridor like the Hallway_01 concept, built from instances of
the kit pieces (run hallway_kit.py first). Not exported - only for checking the look in Blender.
"""

import math
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402

src = {o.name: o for o in bpy.data.collections["Kit_Hallway"].objects}
prev = hg.collection("Preview")
for o in list(prev.objects):
    bpy.data.objects.remove(o)
bpy.context.view_layer.layer_collection.children["Kit_Hallway"].exclude = True

OX = 100.0  # away from the kit row


def put(name, loc, rot_z=0.0, mat=None):
    o = src[name].copy()
    if mat:
        o.data = src[name].data.copy()
        o.data.materials[0] = hg.material(mat)
    o.location = Vector(loc)
    o.rotation_euler = (0, 0, math.radians(rot_z))
    prev.objects.link(o)
    return o


# Corridor along +X, 3.6 m wide (Y -1.8..1.8), 5.2 m long, chained door between two narrow windows at the end.
for x in range(5):
    for y in (-1.5, -0.5, 0.5, 1.5):
        put("SM_Floor_Planks_100", (OX + x + 0.5, y, 0))
        put("SM_Ceiling_100", (OX + x + 0.5, y, 2.8))
put("SM_Wall_Door_160", (OX + 0, -1.8, 0)); put("SM_Wall_200", (OX + 1.6, -1.8, 0)); put("SM_Wall_Door_160", (OX + 3.6, -1.8, 0))
put("SM_Wall_200", (OX + 0, 1.8, 0)); put("SM_Wall_Door_160", (OX + 2.0, 1.8, 0)); put("SM_Wall_Door_160", (OX + 3.6, 1.8, 0))
# End wall runs along +Y after the 90 degree turn; its pivot is at its -Y end.
put("SM_Wall_WindowNarrow_100", (OX + 5.2, -1.8, 0), 90); put("SM_Wall_Door_160", (OX + 5.2, -0.8, 0), 90)
put("SM_Wall_WindowNarrow_100", (OX + 5.2, 0.8, 0), 90)
# Door leaf: the exported leaf runs along -Y in Blender (+Y in Unreal), so the hinge is at the opening's
# +Y edge (0.8 - 0.2). Chains face the corridor (-X).
hinge = Vector((OX + 5.2, 0.6, 0))
put("SM_Door_Panel", hinge); put("SM_ChainedDoor_Chains", hinge)
# Padlocks hang on the chains (points on the chain lines of SM_ChainedDoor_Chains), the green one at the crossing.
for y, z, col in ((0.35, 1.78, "PaintRed"), (0.95, 1.69, "PaintYellow"), (0.55, 0.88, "PaintBlue")):
    put("SM_Padlock", hinge + Vector((-0.08, -y, z)), mat=col)
put("SM_Padlock_Big", hinge + Vector((-0.09, -0.74, 1.65)))
put("SM_SpiderWeb", hinge + Vector((-0.11, -0.74, 1.45)))
put("SM_CoatRack", (OX + 4.6, -1.4, 0))
put("SM_PhoneTable", (OX + 4.75, 1.45, 0)); put("SM_RotaryPhone", (OX + 4.75, 1.4, 0.8), 180)
put("SM_WallSconce", (OX + 4.9, -1.69, 1.85), 180); put("SM_WallSconce", (OX + 4.9, 1.69, 1.85), 0)
put("SM_PhotoFrame", (OX + 1.2, -1.69, 1.6), 180); put("SM_PhotoFrame", (OX + 2.8, 1.69, 1.55))
for x in (1.2, 3.6):
    put("SM_CeilingLamp", (OX + x, 0, 2.8))
put("SM_Rug_Runner", (OX + 2.4, 0, 0)); put("SM_Rug_Runner", (OX + 3.9, 0, 0))

cam_data = bpy.data.cameras.get("PreviewCam") or bpy.data.cameras.new("PreviewCam")
cam_data.lens = 16
cam = bpy.data.objects.new("PreviewCam", cam_data)
prev.objects.link(cam)
cam.location = (OX + 0.4, 0, 1.55)
cam.rotation_euler = (math.radians(88), 0, math.radians(-90))
bpy.context.scene.camera = cam
for n, loc, energy in (("PrevLight1", (OX + 4.6, 0, 2.5), 150), ("PrevLight2", (OX + 1.5, 0, 2.5), 90)):
    ld = bpy.data.lights.get(n) or bpy.data.lights.new(n, "POINT")
    ld.energy = energy
    ld.color = (1, 0.8, 0.55)
    lo = bpy.data.objects.new(n, ld)
    prev.objects.link(lo)
    lo.location = loc
print("preview built:", len(prev.objects), "objects")
