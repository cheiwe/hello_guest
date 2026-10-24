"""
Study kit (Study_Puzzle, Safe_Room concepts): writing desk with a drawer, marble pedestal, tall and low
bookcases filled with books, rolling library ladder, globe, inkwell, thick book, green banker's lamp.
Pivot: centre of the footprint on the floor; front = -X.
"""

import importlib
import math
import os
import random
import sys

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Study")
BOOK_COLORS = ["BookRed", "BookGreen", "BookBlue", "BookBrown", "BookOchre"]


def book_row(prefix, x_front, y0, y1, z, depth, coll, parts, rnd, max_h=0.3):
    """Books standing on a shelf between y0 and y1, spines towards -X; some lean, a few gaps."""
    y = y0 + 0.01
    i = 0
    while y < y1 - 0.03:
        t = rnd.uniform(0.025, 0.06)
        if rnd.random() < 0.08:
            y += rnd.uniform(0.04, 0.1)
            continue
        h = rnd.uniform(0.18, max_h)
        d = depth * rnd.uniform(0.75, 0.95)
        b = hg.box("%s_Bk%d" % (prefix, i), (d, t, h), (x_front + d / 2 + 0.01, y + t / 2, z + h / 2), rnd.choice(BOOK_COLORS), coll, bevel=0.003)
        if rnd.random() < 0.12:
            b.rotation_euler.x = math.radians(rnd.uniform(8, 18))
            b.location.z += 0.01
        parts.append(b)
        y += t + 0.002
        i += 1


def bookcase(name, coll, size=(0.42, 1.2, 2.3), shelves=6, crown=True, seed=1):
    """Wooden bookcase, open front towards -X, books on every shelf, carved top on the tall one."""
    rnd = random.Random(seed)
    d, w, h = size
    parts = [hg.box(name + "_Back", (0.02, w, h), (d / 2 - 0.01, 0, h / 2), "WoodDark", coll)]
    for i, y in enumerate((-w / 2 + 0.02, w / 2 - 0.02)):
        parts.append(hg.box("%s_Side%d" % (name, i), (d, 0.04, h), (0, y, h / 2), "WoodDark", coll, bevel=0.006))
    for i in range(shelves + 1):
        z = 0.08 + i * (h - 0.16) / shelves
        parts.append(hg.box("%s_Shelf%d" % (name, i), (d - 0.02, w - 0.06, 0.03), (0, 0, z), "WoodDark", coll, bevel=0.004))
        if i < shelves:
            book_row("%s_R%d" % (name, i), -d / 2 + 0.01, -w / 2 + 0.04, w / 2 - 0.04, z + 0.015, d - 0.06, coll, parts, rnd,
                     max_h=min(0.32, (h - 0.16) / shelves - 0.04))
    parts.append(hg.box(name + "_Plinth", (d + 0.04, w + 0.04, 0.08), (0, 0, 0.04), "WoodDark", coll, bevel=0.01))
    parts.append(hg.box(name + "_Cornice", (d + 0.06, w + 0.08, 0.07), (-0.01, 0, h + 0.035), "WoodDark", coll, bevel=0.012))
    if crown:
        # Scrolled pediment like the concept: two curved halves rising to a notch in the middle.
        for side in (-1, 1):
            for k in range(6):
                t0, t1 = k / 6, (k + 1) / 6
                y0 = side * (w / 2 - t0 * (w / 2 - 0.08))
                y1 = side * (w / 2 - t1 * (w / 2 - 0.08))
                z0 = h + 0.07 + 0.22 * math.sin(t0 * math.pi * 0.6)
                z1 = h + 0.07 + 0.22 * math.sin(t1 * math.pi * 0.6)
                parts.append(hg.box("%s_Crown%d_%d" % (name, side, k), (0.04, abs(y1 - y0) + 0.01, max(z0, z1) - h - 0.05),
                                    (-d / 2 + 0.03, (y0 + y1) / 2, (h + 0.05 + max(z0, z1)) / 2), "WoodDark", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def writing_desk(name, coll, size=(0.85, 1.6, 0.78)):
    """Heavy desk: thick worn top, pedestal with a door on the right, drawer in the middle, plinth feet."""
    d, w, h = size
    parts = [hg.box(name + "_Top", (d + 0.06, w + 0.08, 0.07), (0, 0, h - 0.035), "WoodWorn", coll, bevel=0.012)]
    hg.jitter(parts[0], 0.004, seed=3)
    ped_w = 0.48
    for i, y in enumerate((-w / 2 + ped_w / 2, w / 2 - ped_w / 2)):
        parts.append(hg.box("%s_Ped%d" % (name, i), (d, ped_w, h - 0.15), (0, y, (h - 0.15) / 2 + 0.08), "WoodWorn", coll, bevel=0.01))
        parts.append(hg.box("%s_Door%d" % (name, i), (0.02, ped_w - 0.1, h - 0.32), (-d / 2 - 0.005, y, (h - 0.15) / 2 + 0.08), "WoodDark", coll, bevel=0.006))
        parts.append(hg.box("%s_Panel%d" % (name, i), (0.015, ped_w - 0.2, h - 0.45), (-d / 2 - 0.015, y, (h - 0.15) / 2 + 0.08), "WoodWorn", coll, bevel=0.006))
        for k, yy in enumerate((y - ped_w / 2 + 0.06, y + ped_w / 2 - 0.06)):
            parts.append(hg.box("%s_Foot%d_%d" % (name, i, k), (d + 0.04, 0.1, 0.09), (0, yy, 0.045), "WoodDark", coll, bevel=0.015))
    parts.append(hg.box(name + "_Apron", (d - 0.04, w - 2 * ped_w, 0.12), (0, 0, h - 0.13), "WoodWorn", coll, bevel=0.006))
    parts.append(hg.box(name + "_Drawer", (0.02, w - 2 * ped_w - 0.12, 0.09), (-d / 2 + 0.01, 0, h - 0.13), "WoodDark", coll, bevel=0.005))
    parts.append(hg.sphere(name + "_Knob", 0.022, (-d / 2 - 0.02, 0, h - 0.13), "WoodDark", coll, segments=10, rings=5))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def pedestal(name, coll, height=1.05):
    """Marble column with an Ionic capital (volutes), square base and a top slab for the bust."""
    parts = [hg.box(name + "_Base", (0.42, 0.42, 0.1), (0, 0, 0.05), "Marble", coll, bevel=0.015)]
    parts.append(hg.cylinder(name + "_Torus", 0.17, 0.08, (0, 0, 0.14), "Marble", coll, segments=24))
    shaft_h = height - 0.38
    parts.append(hg.cylinder(name + "_Shaft", 0.13, shaft_h, (0, 0, 0.18 + shaft_h / 2), "Marble", coll, segments=24, radius_top=0.115))
    # Flutes: shallow vertical grooves as thin darker strips.
    for i in range(12):
        a = 2 * math.pi * i / 12
        f = hg.box("%s_Flute%d" % (name, i), (0.012, 0.012, shaft_h - 0.06), (math.cos(a) * 0.123, math.sin(a) * 0.123, 0.18 + shaft_h / 2), "MarbleDark", coll)
        f.rotation_euler.z = a
        parts.append(f)
    cap_z = 0.18 + shaft_h
    parts.append(hg.box(name + "_Echinus", (0.3, 0.3, 0.07), (0, 0, cap_z + 0.035), "Marble", coll, bevel=0.02))
    for side in (-1, 1):
        parts.append(hg.torus("%s_Volute%d" % (name, side), 0.045, 0.022, (0, side * 0.16, cap_z + 0.05), "Marble", coll,
                              rotation=(math.radians(90), 0, 0), scale=(1, 1, 1)))
    parts.append(hg.box(name + "_Top", (0.4, 0.4, 0.08), (0, 0, height - 0.04), "Marble", coll, bevel=0.012))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def library_ladder(name, coll, height=2.2, width=0.45):
    """Leaning ladder on two wheels (Study_Puzzle). Pivot at the wheels; leans towards +X (the bookcase)."""
    lean = math.radians(14)
    parts = []
    for i, y in enumerate((-width / 2, width / 2)):
        rail = hg.box("%s_Rail%d" % (name, i), (0.05, 0.04, height), (math.sin(lean) * height / 2, y, math.cos(lean) * height / 2), "WoodDark", coll, bevel=0.008)
        rail.rotation_euler.y = lean
        parts.append(rail)
        parts.append(hg.cylinder("%s_Wheel%d" % (name, i), 0.05, 0.03, (0, y, 0.05), "MetalDark", coll, segments=14, rotation=(math.radians(90), 0, 0)))
    steps = 8
    for k in range(steps):
        t = (k + 0.7) / steps
        rung = hg.box("%s_Rung%d" % (name, k), (0.09, width, 0.03), (math.sin(lean) * height * t, 0, math.cos(lean) * height * t), "WoodDark", coll, bevel=0.006)
        parts.append(rung)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def globe(name, coll, height=0.55):
    """Desk globe on a brass meridian and a wooden foot (Study_Puzzle, Safe_Room)."""
    r = 0.17
    parts = [hg.cylinder(name + "_Foot", 0.12, 0.04, (0, 0, 0.02), "WoodDark", coll, segments=20, radius_top=0.09)]
    parts.append(hg.cylinder(name + "_Stem", 0.018, 0.12, (0, 0, 0.1), "WoodDark", coll, segments=10))
    centre = (0, 0, height - r - 0.02)
    ball = hg.sphere(name + "_Ball", r, centre, "Globe", coll, segments=24, rings=12)
    ball.rotation_euler.x = math.radians(23)
    parts.append(ball)
    ring = hg.torus(name + "_Meridian", r + 0.02, 0.008, centre, "Brass", coll, rotation=(math.radians(90), math.radians(23), 0), segments=24)
    parts.append(ring)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    # The map wraps the ball: longitude/latitude UVs around the centre on the M_Globe faces.
    from mathutils import Vector as _V
    mesh = obj.data
    uv = mesh.uv_layers.active.data
    globe_index = mesh.materials.find("M_Globe")
    c = _V(centre)
    for poly in mesh.polygons:
        if poly.material_index != globe_index:
            continue
        for li in poly.loop_indices:
            p = (mesh.vertices[mesh.loops[li].vertex_index].co - c).normalized()
            u = 0.5 + math.atan2(p.y, p.x) / (2 * math.pi)
            v = 0.5 + math.asin(max(-1.0, min(1.0, p.z))) / math.pi
            uv[li].uv = (u, v)
    return obj


def inkwell(name, coll):
    parts = [hg.box(name + "_Bottle", (0.09, 0.09, 0.07), (0, 0, 0.035), "Glass", coll, bevel=0.02)]
    parts.append(hg.box(name + "_Ink", (0.075, 0.075, 0.045), (0, 0, 0.03), "Ink", coll, bevel=0.015))
    parts.append(hg.cylinder(name + "_Neck", 0.022, 0.025, (0, 0, 0.08), "Glass", coll, segments=12))
    parts.append(hg.cylinder(name + "_Cap", 0.03, 0.022, (0, 0, 0.1), "MetalDark", coll, segments=14))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def thick_book(name, coll):
    """Old leather book lying flat: covers, page block, raised bands on the spine."""
    w, d, t = 0.34, 0.26, 0.09
    parts = [hg.box(name + "_Pages", (w - 0.02, d - 0.02, t - 0.02), (0.01, 0, t / 2), "Paper", coll, bevel=0.004)]
    for i, z in enumerate((0.007, t - 0.007)):
        parts.append(hg.box("%s_Cover%d" % (name, i), (w, d, 0.014), (0, 0, z), "Leather", coll, bevel=0.005))
    parts.append(hg.box(name + "_Spine", (0.02, d, t), (-w / 2 + 0.008, 0, t / 2), "Leather", coll, bevel=0.008))
    for k in range(4):
        parts.append(hg.box("%s_Band%d" % (name, k), (0.026, 0.012, t + 0.004), (-w / 2 + 0.006, -d / 2 + 0.05 + k * 0.053, t / 2), "Leather", coll, bevel=0.003))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def bankers_lamp(name, coll):
    """Green banker's lamp (Study_Puzzle)."""
    parts = [hg.cylinder(name + "_Base", 0.09, 0.03, (0, 0, 0.015), "Brass", coll, segments=20)]
    parts.append(hg.rod(name + "_Stem", (0.04, 0, 0.03), (0.04, 0, 0.33), 0.01, "Brass", coll))
    parts.append(hg.rod(name + "_Arm", (0.04, 0, 0.33), (-0.02, 0, 0.36), 0.009, "Brass", coll))
    shade = hg.cylinder(name + "_Shade", 0.06, 0.32, (-0.03, 0, 0.36), "GlassGreen", coll, segments=16)
    shade.rotation_euler.x = math.radians(90)
    shade.scale = (1.0, 1.0, 1.0)
    parts.append(shade)
    obj = hg.join(parts, name)
    # Half-cylinder shade: drop the lower half of the cylinder.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    cut = [f for f in bm.faces if f.material_index == obj.data.materials.find("M_GlassGreen") and f.calc_center_median().z < 0.355]
    bmesh.ops.delete(bm, geom=cut, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    hg.world_uv(obj, scale=4.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Study")
    assets = [
        writing_desk("SM_Desk_Writing", coll),
        pedestal("SM_Pedestal_Marble", coll),
        bookcase("SM_Bookcase_Tall", coll, seed=1),
        bookcase("SM_Bookcase_Low", coll, size=(0.38, 1.0, 1.1), shelves=2, crown=False, seed=2),
        library_ladder("SM_LibraryLadder", coll),
        globe("SM_Globe", coll),
        inkwell("SM_Inkwell", coll),
        thick_book("SM_Book_Thick", coll),
        bankers_lamp("SM_Lamp_Bankers", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.5) + 0.6
    hg.save_blend(os.path.join(OUT, "Study_Kit.blend"))
    print("exported %d study assets to %s" % (len(assets), OUT))


build()
