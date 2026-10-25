"""
Yard junk and the player's house (Yard_01-03, Street_Example).

Yard: rusty oil barrels (standing, lying), firewood pile, wheelbarrow with weeds, coiled garden hose,
shovel, rake, wooden ladder, tree stump, a heap of broken planks.
Player's house: the cream clapboard cottage across the street (Street_Example, left): one storey with
an attic gable, brown shingle roof, little gabled porch with posts and steps, chimney, sash windows
with trim, gutters. An exterior shell to dress the street; the player's room is the interior kit.
Front of the house faces -Y (towards the street); pivot at the bottom centre of the front wall.
"""

import importlib
import math
import os
import random
import sys

import bmesh
import bpy

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Yard")
RX = (math.radians(90), 0, 0)
RY = (0, math.radians(90), 0)


def prism(name, coll, pts_xz, depth, mat, y0=0.0):
    """Extrudes an XZ outline along +Y from y0 (gables, roof ends)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts_xz]
    b = [bm.verts.new((x, y0 + depth, z)) for x, z in pts_xz]
    caps = [bm.faces.new(list(reversed(a))), bm.faces.new(b)]
    n = len(pts_xz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.triangulate(bm, faces=caps)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material(mat))
    coll.objects.link(obj)
    return obj


# --- Yard props --------------------------------------------------------------------------------------

def barrel_parts(name, coll, loc=(0, 0, 0), lying=False, rot=0.0):
    """200 l oil drum: rusty body, two rolling hoops, rim, a bung on the lid."""
    r, h = 0.29, 0.88
    parts = [hg.cylinder(name + "_Body", r, h, (0, 0, h / 2), "MetalRust", coll, segments=20)]
    for k, z in enumerate((0.02, h * 0.33, h * 0.66, h - 0.02)):
        parts.append(hg.torus("%s_Hoop%d" % (name, k), r + 0.004, 0.012, (0, 0, z), "MetalRust", coll, segments=20, ring_segments=5))
    parts.append(hg.cylinder(name + "_Bung", 0.03, 0.02, (0.15, 0, h + 0.01), "MetalDark", coll, segments=8))
    for o in parts:
        if lying:
            o.location.z -= h / 2
            o.location.rotate(__import__("mathutils").Euler((0, math.radians(90), 0)))
            o.rotation_euler.y += math.radians(90)
            o.location.z += r
        hg.rotate_about_z(o, rot)
        o.location.x += loc[0]
        o.location.y += loc[1]
        o.location.z += loc[2]
    return parts


def barrel(name, coll, lying=False):
    obj = hg.join(barrel_parts(name, coll, lying=lying), name)
    hg.world_uv(obj)
    return obj


def firewood(name, coll, seed=1):
    """Stack of split logs against a fence, ends showing the light wood."""
    rnd = random.Random(seed)
    parts = []
    for row in range(4):
        for k in range(5 - row):
            y = (k - (4 - row) / 2) * 0.2 + rnd.uniform(-0.02, 0.02)
            z = 0.09 + row * 0.16
            log = hg.cylinder("%s_L%d%d" % (name, row, k), rnd.uniform(0.07, 0.1), rnd.uniform(0.7, 0.85), (rnd.uniform(-0.05, 0.05), y, z), "Bark", coll, segments=8, rotation=RY)
            hg.jitter(log, 0.008, seed=row * 10 + k)
            parts.append(log)
            for sgn in (-1, 1):
                parts.append(hg.cylinder("%s_E%d%d%d" % (name, row, k, sgn), 0.065, 0.01, (log.location.x + sgn * log.dimensions.z / 2, y, z), "WoodWorn", coll, segments=8, rotation=RY))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def wheelbarrow(name, coll):
    """Rusty wheelbarrow with a weedy load: tapered tray, front wheel, two handles, legs. Front +X."""
    parts = []
    tray = hg.box(name + "_Tray", (0.75, 0.6, 0.28), (0.1, 0, 0.52), "MetalRust", coll, bevel=0.06)
    for v in tray.data.vertices:
        if v.co.z < 0:
            v.co.x *= 0.7
            v.co.y *= 0.65
    parts.append(tray)
    parts.append(hg.box(name + "_Soil", (0.62, 0.5, 0.04), (0.1, 0, 0.64), "Mud", coll))
    parts.append(hg.cylinder(name + "_Wheel", 0.2, 0.08, (0.62, 0, 0.2), "Rubber", coll, segments=18, rotation=RX))
    parts.append(hg.cylinder(name + "_Hub", 0.06, 0.1, (0.62, 0, 0.2), "MetalDark", coll, segments=10, rotation=RX))
    for k, y in enumerate((-0.22, 0.22)):
        parts.append(hg.rod("%s_Handle%d" % (name, k), (0.62, y * 0.4, 0.2), (-0.75, y * 1.25, 0.6), 0.02, "WoodWorn", coll))
        parts.append(hg.rod("%s_Leg%d" % (name, k), (-0.25, y * 0.9, 0.42), (-0.3, y * 0.95, 0.0), 0.015, "MetalRust", coll, segments=6))
    rnd = random.Random(3)
    for k in range(14):
        x, y = rnd.uniform(-0.15, 0.35), rnd.uniform(-0.2, 0.2)
        parts.append(hg.rod("%s_Weed%d" % (name, k), (x, y, 0.64), (x + rnd.uniform(-0.1, 0.1), y + rnd.uniform(-0.1, 0.1), 0.64 + rnd.uniform(0.15, 0.4)), 0.006, "Grass", coll, segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def hose_coil(name, coll):
    """Green garden hose lying in loose loops, with a brass nozzle."""
    pts = []
    for i in range(60):
        t = i / 59 * 4 * 2 * math.pi
        r = 0.28 + 0.02 * math.sin(t * 1.7) + 0.015 * (i % 7) / 7
        pts.append((r * math.cos(t), r * math.sin(t), 0.018 + 0.012 * (i / 59)))
    pts.append((0.6, 0.15, 0.018))
    parts = [hg.cable(name + "_Hose", pts, 0.016, "HoseGreen", coll, segments=8, resolution=3)]
    parts.append(hg.cylinder(name + "_Nozzle", 0.02, 0.1, (0.65, 0.16, 0.02), "Brass", coll, segments=10, rotation=RY))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def shovel(name, coll):
    """Long-handled shovel, lying along X (lean it against a wall in the level)."""
    parts = [hg.cylinder(name + "_Shaft", 0.018, 1.1, (0.0, 0, 0.02), "WoodWorn", coll, segments=8, rotation=RY)]
    parts.append(hg.box(name + "_Grip", (0.04, 0.14, 0.03), (-0.56, 0, 0.02), "WoodWorn", coll, bevel=0.01))
    blade = hg.box(name + "_Blade", (0.3, 0.24, 0.012), (0.7, 0, 0.02), "MetalRust", coll, bevel=0.004)
    for v in blade.data.vertices:
        if v.co.x > 0:
            v.co.y *= 0.6
            v.co.z += 0.03
    parts.append(blade)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def rake(name, coll):
    parts = [hg.cylinder(name + "_Shaft", 0.016, 1.4, (0.0, 0, 0.02), "WoodWorn", coll, segments=8, rotation=RY)]
    parts.append(hg.box(name + "_Head", (0.03, 0.4, 0.03), (0.72, 0, 0.02), "MetalRust", coll))
    for k in range(10):
        parts.append(hg.rod("%s_Tine%d" % (name, k), (0.72, -0.18 + k * 0.04, 0.02), (0.76, -0.18 + k * 0.04, -0.06), 0.004, "MetalRust", coll, segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def ladder(name, coll, height=3.0):
    """Wooden ladder standing on Z=0 (lean it with a small pitch), rungs every 30 cm."""
    parts = []
    for k, x in enumerate((-0.22, 0.22)):
        parts.append(hg.box("%s_Rail%d" % (name, k), (0.05, 0.08, height), (x, 0, height / 2), "WoodWeathered", coll, bevel=0.006))
    for k in range(int(height / 0.3)):
        parts.append(hg.cylinder("%s_Rung%d" % (name, k), 0.018, 0.44, (0, 0, 0.25 + k * 0.3), "WoodWeathered", coll, segments=8, rotation=RY))
    obj = hg.join(parts, name)
    hg.jitter(obj, 0.003, seed=2)
    hg.world_uv(obj)
    return obj


def stump(name, coll):
    """Old tree stump with root flares and a cut top showing the rings."""
    parts = [hg.cylinder(name + "_Trunk", 0.35, 0.45, (0, 0, 0.225), "Bark", coll, segments=16, radius_top=0.3)]
    parts.append(hg.cylinder(name + "_Top", 0.29, 0.02, (0, 0, 0.455), "WoodWorn", coll, segments=16))
    for k in range(3):
        parts.append(hg.torus("%s_Ring%d" % (name, k), 0.07 + k * 0.07, 0.006, (0, 0, 0.467), "WoodDark", coll, segments=16, ring_segments=4))
    for k in range(5):
        a = k * 2 * math.pi / 5
        parts.append(hg.cable("%s_Root%d" % (name, k), [(0.2 * math.cos(a), 0.2 * math.sin(a), 0.3), (0.42 * math.cos(a), 0.42 * math.sin(a), 0.08), (0.65 * math.cos(a + 0.2), 0.65 * math.sin(a + 0.2), -0.03)],
                              0.09, "Bark", coll, segments=8, resolution=4, radii=[1.0, 0.7, 0.3]))
    obj = hg.join(parts, name)
    hg.jitter(obj, 0.01, seed=5)
    hg.world_uv(obj)
    return obj


def plank_heap(name, coll, seed=9):
    """Broken planks and a bent sheet of corrugated iron thrown in a heap (Yard_01, middle)."""
    rnd = random.Random(seed)
    parts = []
    for k in range(8):
        p = hg.box("%s_P%d" % (name, k), (rnd.uniform(0.8, 1.6), 0.14, 0.025), (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0.03 + k * 0.03), rnd.choice(("WoodWeathered", "WoodWorn")), coll,
                   bevel=0.004, rotation=(rnd.uniform(-0.25, 0.25), rnd.uniform(-0.2, 0.2), rnd.uniform(0, math.pi)))
        hg.jitter(p, 0.005, seed=k)
        parts.append(p)
    sheet = hg.box(name + "_Iron", (0.9, 0.6, 0.01), (0.2, 0.1, 0.3), "MetalRust", coll, rotation=(0.3, -0.2, 0.6))
    mod = sheet.modifiers.new("Sub", "SUBSURF")
    mod.subdivision_type = "SIMPLE"
    mod.levels = 4
    bpy.ops.object.select_all(action="DESELECT")
    sheet.select_set(True)
    bpy.context.view_layer.objects.active = sheet
    bpy.ops.object.modifier_apply(modifier="Sub")
    for v in sheet.data.vertices:
        v.co.z += 0.02 * math.sin(v.co.x * 40)
    parts.append(sheet)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


# --- Player's house ------------------------------------------------------------------------------------

def clapboards(name, coll, x0, x1, z0, z1, y, face, mat="SidingCream"):
    """Overlapping horizontal boards on a wall face at y (face: -1 faces -Y, +1 faces +Y)."""
    parts = []
    step = 0.16
    z = z0
    k = 0
    while z < z1 - 0.01:
        h = min(step + 0.02, z1 - z)
        b = hg.box("%s_%d" % (name, k), (x1 - x0, 0.03, h), ((x0 + x1) / 2, y + face * 0.015, z + h / 2), mat, coll)
        for v in b.data.vertices:
            if v.co.z < 0:
                v.co.y += face * 0.012        # bottom edge sticks out: lap siding
        parts.append(b)
        z += step
        k += 1
    return parts


def sash(name, coll, x, z, y, face, w=0.9, h=1.3):
    """Window with trim, two panes and a sill on a wall face."""
    parts = []
    t = 0.09
    yo = y + face * 0.05
    for i, (sx, sz, px, pz) in enumerate(((w + 2 * t, t, x, z + h + t / 2), (t, h, x - w / 2 - t / 2, z + h / 2), (t, h, x + w / 2 + t / 2, z + h / 2))):
        parts.append(hg.box("%s_Trim%d" % (name, i), (sx, 0.05, sz), (px, yo, pz), "Trim", coll, bevel=0.008))
    parts.append(hg.box(name + "_Sill", (w + 0.3, 0.1, 0.05), (x, yo + face * 0.03, z - 0.02), "Trim", coll, bevel=0.01))
    parts.append(hg.box(name + "_Glass", (w, 0.02, h), (x, y + face * 0.02, z + h / 2), "WindowDark", coll))
    parts.append(hg.box(name + "_Rail", (w, 0.04, 0.05), (x, y + face * 0.04, z + h / 2), "Trim", coll))
    parts.append(hg.box(name + "_Mull", (0.04, 0.04, h), (x, y + face * 0.04, z + h / 2), "Trim", coll))
    return parts


def side_boards(name, coll, x, y0, y1, z0, z1, side):
    """Clapboards on a side wall at x (side -1 faces -X, +1 faces +X), running along Y."""
    out = []
    for b in clapboards(name, coll, y0, y1, z0, z1, 0.0, -1):
        b.location = (x, b.location.x, b.location.z)
        b.rotation_euler.z = math.radians(90 * side)
        out.append(b)
    return out


def side_window(name, coll, x, y, z, side, w=0.9, h=1.3):
    out = []
    for o in sash(name, coll, 0, z, 0, -1, w=w, h=h):
        o.location = (x + side * (-o.location.y), y + o.location.x, o.location.z)
        o.rotation_euler.z = math.radians(90 * side)
        out.append(o)
    return out


def player_house(name, coll, w=6.6, d=8.5, wall_h=3.0, ridge=2.6):
    """Front gable towards the street (-Y) like the cottage in Street_Example: porch hood under the
    gable, attic window in the gable, ridge running back along +Y."""
    parts = []
    z0, z1 = 0.5, 0.45 + wall_h
    parts.append(hg.box(name + "_Core", (w - 0.1, d - 0.1, wall_h), (0, d / 2, 0.45 + wall_h / 2), "Plaster", coll))
    parts.append(hg.box(name + "_Base", (w + 0.1, d + 0.1, 0.5), (0, d / 2, 0.25), "Concrete", coll, bevel=0.02))
    parts += clapboards(name + "_SidF", coll, -w / 2, w / 2, z0, z1, 0.0, -1)
    parts += clapboards(name + "_SidB", coll, -w / 2, w / 2, z0, z1, d, 1)
    for side, x in ((-1, -w / 2), (1, w / 2)):
        parts += side_boards("%s_SidS%d" % (name, side), coll, x, 0.0, d, z0, z1, side)
    # Gables front and back, sided with the same boards (clipped to the triangle by tapering).
    for k, (y0, face) in enumerate(((0.0, -1), (d, 1))):
        tri = prism("%s_Gable%d" % (name, k), coll, [(-w / 2, z1), (w / 2, z1), (0.0, z1 + ridge)], 0.1, "SidingCream", y0=y0 - 0.1 if face < 0 else y0)
        parts.append(tri)
        zz = z1 + 0.16
        while zz < z1 + ridge - 0.3:
            half = (w / 2) * (1 - (zz - z1) / ridge)
            b = hg.box("%s_GB%d_%.2f" % (name, k, zz), (2 * half - 0.1, 0.03, 0.18), (0, y0 + face * 0.115, zz), "SidingCream", coll)
            parts.append(b)
            zz += 0.16
    for x in (-w / 2, w / 2):
        for y in (0.0, d):
            parts.append(hg.box(name + "_Corner%.0f%.0f" % (x, y), (0.12, 0.12, wall_h + 0.05), (x, y, 0.45 + wall_h / 2), "Trim", coll))
    # Roof: two slopes falling to the sides, overhangs, ridge cap, barge boards on the gables.
    over = 0.4
    half = w / 2 + over
    slope = math.atan2(ridge, w / 2)
    length = half / math.cos(slope)
    for k, sgn in enumerate((-1, 1)):
        roof = hg.box("%s_Roof%d" % (name, k), (length, d + 2 * over, 0.12), (0, 0, 0), "ShingleBrown", coll)
        roof.rotation_euler.y = sgn * slope
        roof.location = (sgn * half / 2, d / 2, z1 + ridge - (half / 2) * math.tan(slope) + 0.06)
        parts.append(roof)
        for j, y in enumerate((-over + 0.02, d + over - 0.02)):
            barge = hg.box("%s_Barge%d%d" % (name, k, j), (length, 0.05, 0.2), (sgn * half / 2, y, z1 + ridge - (half / 2) * math.tan(slope) - 0.02), "Trim", coll)
            barge.rotation_euler.y = sgn * slope
            parts.append(barge)
    parts.append(hg.box(name + "_Ridge", (0.22, d + 2 * over, 0.1), (0, d / 2, z1 + ridge + 0.1), "ShingleBrown", coll, bevel=0.03))
    parts.append(hg.box(name + "_Chimney", (0.6, 0.6, 2.4), (w / 4, d * 0.3, z1 + 1.5), "Brick", coll))
    parts.append(hg.box(name + "_ChimneyCap", (0.72, 0.72, 0.1), (w / 4, d * 0.3, z1 + 2.75), "Concrete", coll))
    # Front: door off-centre under a small gabled porch hood on two posts, three steps.
    door_x = 0.9
    parts.append(hg.box(name + "_Door", (1.0, 0.06, 2.1), (door_x, -0.05, 0.5 + 1.05), "WoodPainted", coll, bevel=0.01))
    parts.append(hg.sphere(name + "_Knob", 0.03, (door_x + 0.38, -0.1, 1.5), "Brass", coll, segments=8, rings=4))
    for k in range(3):
        parts.append(hg.box("%s_Step%d" % (name, k), (1.6, 0.35, 0.17), (door_x, -0.15 - k * 0.3, 0.085 + (2 - k) * 0.17), "WoodWeathered", coll, bevel=0.01))
    for k, x in enumerate((door_x - 0.75, door_x + 0.75)):
        parts.append(hg.box("%s_Post%d" % (name, k), (0.1, 0.1, 2.3), (x, -1.0, 0.5 + 1.15), "Trim", coll, bevel=0.01))
    parts.append(prism(name + "_Hood", coll, [(door_x - 0.95, 2.85), (door_x + 0.95, 2.85), (door_x, 3.55)], 1.15, "ShingleBrown", y0=-1.15))
    parts.append(prism(name + "_HoodGable", coll, [(door_x - 0.8, 2.85), (door_x + 0.8, 2.85), (door_x, 3.42)], 0.05, "SidingCream", y0=-1.16))
    parts += sash(name + "_WinF0", coll, -1.6, 1.3, 0.0, -1)
    parts += sash(name + "_WinAttic", coll, 0.0, z1 + 0.45, -0.1, -1, w=0.6, h=0.85)
    parts += sash(name + "_WinB0", coll, 0.0, 1.3, d, 1)
    for side, x in ((-1, -w / 2), (1, w / 2)):
        for k, y in enumerate((1.6, 4.25, 6.9)):
            # The player's room looks out of the big -X window in the middle (onto the street).
            big = side < 0 and k == 1
            parts += side_window("%s_WinS%d_%d" % (name, side, k), coll, x, y, 1.1 if big else 1.3, side, w=1.4 if big else 0.9, h=1.55 if big else 1.3)
    for k, sgn in enumerate((-1, 1)):
        parts.append(hg.cylinder("%s_Gutter%d" % (name, k), 0.06, d + 2 * over, (sgn * (w / 2 + over - 0.05), d / 2, z1 - over * math.tan(slope) + 0.02), "MetalPainted", coll, segments=10, rotation=RX))
    parts.append(hg.cylinder(name + "_Downpipe", 0.04, wall_h, (-w / 2 - 0.35, 0.15, 0.5 + wall_h / 2), "MetalPainted", coll, segments=8))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Yard")
    assets = [
        barrel("SM_Barrel_Rust", coll),
        barrel("SM_Barrel_Rust_Lying", coll, lying=True),
        firewood("SM_Firewood_Pile", coll),
        wheelbarrow("SM_Wheelbarrow", coll),
        hose_coil("SM_Hose_Coil", coll),
        shovel("SM_Shovel", coll),
        rake("SM_Rake", coll),
        ladder("SM_Ladder_Wood", coll),
        stump("SM_Stump", coll),
        plank_heap("SM_Planks_Heap", coll),
        player_house("SM_PlayerHouse", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x + obj.dimensions.x / 2
        x += max(obj.dimensions.x, 0.5) + 0.8
    hg.save_blend(os.path.join(OUT, "Yard_Kit.blend"))
    print("exported %d yard assets to %s" % (len(assets), OUT))


build()
