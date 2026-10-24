"""
Hallway kit of the neighbour house (concepts Hallway_01, Hallway_02, Hallway_simple).

Builds every piece at the origin, exports it to SourceArt/Models/Hallway/<name>.fbx and then lays the
pieces out in a row for review. Run in Blender:
    exec(open(r"<project>/Scripts/Blender/assets/hallway_kit.py", encoding="utf-8").read())
"""

import importlib
import math
import os
import random
import sys

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

from mathutils import Vector  # noqa: E402

OUT = os.path.join(hg.MODELS_DIR, "Hallway")

WALL_H = 2.8      # floor to ceiling, matches the blockout (F1 40 cm -> slab 320 cm)
WALL_T = 0.20
PANEL_H = 0.95    # wainscot height
DOOR_W = 1.2      # opening width (the Guest needs it)
DOOR_H = 2.5


def wall_face(prefix, x0, x1, y, facing, coll, parts, z0=0.0, z1=WALL_H):
    """Wainscot, wallpaper, baseboard and crown molding on one face of a wall between x0 and x1."""
    s = -1 if facing < 0 else 1
    width = x1 - x0
    cx = (x0 + x1) / 2
    if z0 < PANEL_H:
        top = min(PANEL_H, z1)
        parts.append(hg.box(prefix + "_Panel", (width, 0.02, top - z0), (cx, y + s * 0.01, (z0 + top) / 2), "WoodPanel", coll))
        # Vertical board grooves of the wainscot.
        board = 0.16
        n = int(width / board)
        for i in range(1, n):
            gx = x0 + i * width / n
            parts.append(hg.box(prefix + "_Groove%d" % i, (0.012, 0.006, top - z0 - 0.08), (gx, y + s * 0.021, (z0 + top) / 2), "WoodDark", coll))
        # Chair rail on top of the wainscot.
        if z1 > PANEL_H:
            parts.append(hg.box(prefix + "_Rail", (width, 0.05, 0.05), (cx, y + s * 0.025, PANEL_H), "WoodDark", coll, bevel=0.008))
    if z1 > PANEL_H:
        bottom = max(PANEL_H, z0)
        parts.append(hg.box(prefix + "_Paper", (width, 0.004, z1 - bottom), (cx, y + s * 0.002, (bottom + z1) / 2), "Wallpaper", coll))
    if z0 <= 0.0:
        parts.append(hg.box(prefix + "_Base", (width, 0.03, 0.12), (cx, y + s * 0.03, 0.06), "WoodDark", coll, bevel=0.006))
    if z1 >= WALL_H:
        parts.append(hg.box(prefix + "_Crown", (width, 0.06, 0.08), (cx, y + s * 0.03, WALL_H - 0.04), "WoodDark", coll, bevel=0.01))


def wall_module(name, width, coll):
    """Straight interior wall, both faces dressed. Pivot: bottom-left, runs along +X, centred on Y=0."""
    parts = [hg.box(name + "_Core", (width, WALL_T - 0.05, WALL_H), (width / 2, 0, WALL_H / 2), "Plaster", coll)]
    wall_face(name + "_F", 0, width, -WALL_T / 2 + 0.025, -1, coll, parts)
    wall_face(name + "_B", 0, width, WALL_T / 2 - 0.025, 1, coll, parts)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def door_trim(prefix, x0, x1, top, y, s, coll, parts):
    """Casing around a doorway on one face."""
    t = 0.09
    parts.append(hg.box(prefix + "_L", (t, 0.03, top + t), (x0 - t / 2, y + s * 0.015, (top + t) / 2), "WoodDark", coll, bevel=0.008))
    parts.append(hg.box(prefix + "_R", (t, 0.03, top + t), (x1 + t / 2, y + s * 0.015, (top + t) / 2), "WoodDark", coll, bevel=0.008))
    parts.append(hg.box(prefix + "_T", (x1 - x0 + 2 * t + 0.04, 0.04, t + 0.02), (x0 + (x1 - x0) / 2, y + s * 0.02, top + t / 2 + 0.01), "WoodDark", coll, bevel=0.01))


def door_wall_module(name, width, coll):
    """Wall with a centred doorway (DOOR_W x DOOR_H) and casings on both sides."""
    x0 = (width - DOOR_W) / 2
    x1 = x0 + DOOR_W
    parts = []
    for i, (a, b) in enumerate(((0, x0), (x1, width))):
        parts.append(hg.box(name + "_Core%d" % i, (b - a, WALL_T - 0.05, WALL_H), ((a + b) / 2, 0, WALL_H / 2), "Plaster", coll))
        wall_face(name + "_F%d" % i, a, b, -WALL_T / 2 + 0.025, -1, coll, parts)
        wall_face(name + "_B%d" % i, a, b, WALL_T / 2 - 0.025, 1, coll, parts)
    parts.append(hg.box(name + "_Lintel", (DOOR_W, WALL_T - 0.05, WALL_H - DOOR_H), ((x0 + x1) / 2, 0, (DOOR_H + WALL_H) / 2), "Plaster", coll))
    wall_face(name + "_LF", x0, x1, -WALL_T / 2 + 0.025, -1, coll, parts, z0=DOOR_H)
    wall_face(name + "_LB", x0, x1, WALL_T / 2 - 0.025, 1, coll, parts, z0=DOOR_H)
    # Jambs inside the opening.
    for i, x in enumerate((x0 + 0.015, x1 - 0.015)):
        parts.append(hg.box(name + "_Jamb%d" % i, (0.03, WALL_T, DOOR_H), (x, 0, DOOR_H / 2), "WoodDark", coll))
    parts.append(hg.box(name + "_Head", (DOOR_W, WALL_T, 0.03), ((x0 + x1) / 2, 0, DOOR_H - 0.015), "WoodDark", coll))
    door_trim(name + "_TF", x0, x1, DOOR_H, -WALL_T / 2, -1, coll, parts)
    door_trim(name + "_TB", x0, x1, DOOR_H, WALL_T / 2, 1, coll, parts)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def window_wall_module(name, width, coll, win_w=0.42, sill=0.95, win_h=1.25):
    """Wall with a narrow window (the ones beside the chained door): frame, cross bars, dusty glass."""
    x0 = (width - win_w) / 2
    x1 = x0 + win_w
    top = sill + win_h
    parts = []
    for i, (a, b) in enumerate(((0, x0), (x1, width))):
        parts.append(hg.box(name + "_Core%d" % i, (b - a, WALL_T - 0.05, WALL_H), ((a + b) / 2, 0, WALL_H / 2), "Plaster", coll))
        wall_face(name + "_F%d" % i, a, b, -WALL_T / 2 + 0.025, -1, coll, parts)
        wall_face(name + "_B%d" % i, a, b, WALL_T / 2 - 0.025, 1, coll, parts)
    for i, (z0, z1) in enumerate(((0, sill), (top, WALL_H))):
        parts.append(hg.box(name + "_Fill%d" % i, (win_w, WALL_T - 0.05, z1 - z0), ((x0 + x1) / 2, 0, (z0 + z1) / 2), "Plaster", coll))
        wall_face(name + "_FF%d" % i, x0, x1, -WALL_T / 2 + 0.025, -1, coll, parts, z0=z0, z1=z1)
        wall_face(name + "_FB%d" % i, x0, x1, WALL_T / 2 - 0.025, 1, coll, parts, z0=z0, z1=z1)
    # Frame, sill and the glass with a cross of glazing bars.
    for side in (-1, 1):
        y = side * (WALL_T / 2)
        parts.append(hg.box("%s_FrL%d" % (name, side), (0.05, 0.04, win_h + 0.05), (x0 - 0.025, y, sill + win_h / 2), "Trim", coll, bevel=0.006))
        parts.append(hg.box("%s_FrR%d" % (name, side), (0.05, 0.04, win_h + 0.05), (x1 + 0.025, y, sill + win_h / 2), "Trim", coll, bevel=0.006))
        parts.append(hg.box("%s_FrT%d" % (name, side), (win_w + 0.1, 0.04, 0.05), ((x0 + x1) / 2, y, top + 0.025), "Trim", coll, bevel=0.006))
        parts.append(hg.box("%s_Sill%d" % (name, side), (win_w + 0.14, 0.07, 0.04), ((x0 + x1) / 2, y + side * 0.02, sill - 0.02), "Trim", coll, bevel=0.008))
    parts.append(hg.box(name + "_Glass", (win_w, 0.01, win_h), ((x0 + x1) / 2, 0, sill + win_h / 2), "Glass", coll))
    for i, z in enumerate((sill + win_h / 3, sill + 2 * win_h / 3)):
        parts.append(hg.box("%s_BarH%d" % (name, i), (win_w, 0.03, 0.025), ((x0 + x1) / 2, 0, z), "Trim", coll))
    parts.append(hg.box(name + "_BarV", (0.025, 0.03, win_h), ((x0 + x1) / 2, 0, sill + win_h / 2), "Trim", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def ceiling_lamp(name, coll):
    """Dome ceiling light from Hallway_02. Pivot on the ceiling (Z=0), hangs down."""
    parts = [hg.cylinder(name + "_Base", 0.09, 0.025, (0, 0, -0.0125), "Brass", coll, segments=20)]
    parts.append(hg.cylinder(name + "_Stem", 0.012, 0.06, (0, 0, -0.055), "Brass", coll, segments=8))
    dome = hg.sphere(name + "_Dome", 0.16, (0, 0, -0.1), "LampShade", coll, segments=20, rings=10, scale=(1, 1, 0.45))
    parts.append(dome)
    parts.append(hg.sphere(name + "_Finial", 0.02, (0, 0, -0.17), "Brass", coll, segments=8, rings=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def floor_planks(name, coll, size=1.0, seed=3):
    """1 x 1 m tile of uneven boards with gaps; top at Z = 0."""
    rnd = random.Random(seed)
    parts = []
    board = 0.125
    n = int(round(size / board))
    for i in range(n):
        y = -size / 2 + board * (i + 0.5)
        # Each row is split once at a random point: staggered board ends.
        cut = rnd.uniform(0.25, 0.75) * size
        for j, (a, b) in enumerate(((0, cut), (cut, size))):
            h = rnd.uniform(0.0, 0.006)
            p = hg.box("%s_B%d_%d" % (name, i, j), (b - a - 0.006, board - 0.008, 0.03), (-size / 2 + (a + b) / 2, y, -0.015 + h), "WoodFloor", coll, bevel=0.004)
            p.rotation_euler.z = math.radians(rnd.uniform(-0.4, 0.4))
            parts.append(p)
    parts.append(hg.box(name + "_Sub", (size, size, 0.02), (0, 0, -0.035), "WoodDark", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def ceiling(name, coll, size=1.0):
    obj = hg.box(name, (size, size, 0.02), (0, 0, 0.01), "Plaster", coll)
    hg.world_uv(obj)
    return obj


def door_panel(name, coll):
    """Four-panel door. Pivot at the hinge, bottom; the leaf runs along +Y (as AHGDoor expects), thickness along X."""
    w, h, t = DOOR_W - 0.02, DOOR_H - 0.02, 0.05
    parts = [hg.box(name + "_Leaf", (t, w, h), (0, w / 2, h / 2), "WoodPainted", coll, bevel=0.006)]
    # Raised panels on both faces: 2 columns x 2 rows, the upper ones taller.
    for side in (-1, 1):
        for col in range(2):
            for row, (z0, z1) in enumerate(((0.15, 0.95), (1.1, h - 0.15))):
                y0 = 0.12 + col * (w - 0.12) / 2
                y1 = y0 + (w - 0.36) / 2
                parts.append(hg.box("%s_P%d%d%d" % (name, side, col, row), (0.012, y1 - y0, z1 - z0),
                                    (side * (t / 2 + 0.004), (y0 + y1) / 2, (z0 + z1) / 2), "WoodDark", coll, bevel=0.004))
    # Knob and plate on both sides.
    for side in (-1, 1):
        parts.append(hg.box(name + "_Plate%d" % side, (0.01, 0.05, 0.16), (side * (t / 2 + 0.005), w - 0.1, 1.0), "Brass", coll, bevel=0.003))
        knob = hg.sphere(name + "_Knob%d" % side, 0.03, (side * (t / 2 + 0.04), w - 0.1, 1.0), "Brass", coll)
        neck = hg.cylinder(name + "_Neck%d" % side, 0.01, 0.04, (side * (t / 2 + 0.02), w - 0.1, 1.0), "Brass", coll, rotation=(0, math.radians(90), 0))
        parts += [knob, neck]
    for z in (0.3, h - 0.3):
        parts.append(hg.box(name + "_Hinge%.0f" % (z * 10), (t + 0.01, 0.03, 0.1), (0, 0.015, z), "MetalDark", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    # In Unreal the leaf must run along +Y from the hinge (AHGDoor).
    hg.mirror_y(obj)
    return obj


def chain(name, start, end, coll, link_len=0.09, wire=0.011):
    """
    Chain between two points in the plane of a door (YZ, viewed along X). Links are stretched along the
    chain and alternate between facing the viewer and edge-on, overlapping like real links.
    """
    start, end = Vector(start), Vector(end)
    direction = end - start
    step = link_len * 0.68
    count = max(2, int(direction.length / step) + 1)
    angle = math.atan2(direction.z, direction.y)
    links = []
    for i in range(count):
        p = start + direction * (i / (count - 1))
        # Torus in the XY plane, long axis along Y. "YXZ": first turn about Y (flat-facing links have
        # their normal along X), then about X to follow the chain direction.
        link = hg.torus("%s_L%d" % (name, i), link_len / 2 - wire, wire, p, "Chain", coll, scale=(0.6, 1.0, 1.0), segments=14)
        link.rotation_mode = "YXZ"
        link.rotation_euler = (angle, math.radians(90) if i % 2 == 0 else 0.0, 0.0)
        links.append(link)
    return links


def padlock(name, coll, color, size=1.0):
    """Cartoon padlock: rounded body, shackle, keyhole. Pivot at the shackle top (where it hangs)."""
    s = size
    parts = [hg.box(name + "_Body", (0.05 * s, 0.11 * s, 0.10 * s), (0, 0, -0.13 * s), color, coll, bevel=0.018 * s)]
    shackle = hg.torus(name + "_Shackle", 0.035 * s, 0.009 * s, (0, 0, -0.07 * s), "MetalDark", coll, rotation=(math.radians(90), 0, 0))
    parts.append(shackle)
    parts.append(hg.box(name + "_Hole", (0.006, 0.014 * s, 0.03 * s), (-0.026 * s, 0, -0.14 * s), "MetalDark", coll))
    parts.append(hg.cylinder(name + "_HoleTop", 0.011 * s, 0.006, (-0.026 * s, 0, -0.12 * s), "MetalDark", coll, rotation=(0, math.radians(90), 0)))
    return hg.join(parts, name)


def spider_web(name, coll, radius=0.32, seed=5):
    """Flat web: radial threads and a spiral, as thin boxes in the YZ plane."""
    rnd = random.Random(seed)
    parts = []
    spokes = 9
    for i in range(spokes):
        a = 2 * math.pi * i / spokes + rnd.uniform(-0.15, 0.15)
        r = radius * rnd.uniform(0.6, 1.15)
        mid = Vector((0, math.cos(a) * r / 2, math.sin(a) * r / 2))
        p = hg.box("%s_S%d" % (name, i), (0.002, r, 0.004), mid, "Web", coll)
        p.rotation_euler.x = a
        parts.append(p)
    for ring in range(1, 6):
        r = radius * ring / 6
        for i in range(spokes):
            # Torn web: some spiral segments are missing.
            if rnd.random() < 0.18:
                continue
            a0 = 2 * math.pi * i / spokes
            a1 = 2 * math.pi * (i + 1) / spokes
            p0 = Vector((0, math.cos(a0) * r, math.sin(a0) * r))
            p1 = Vector((0, math.cos(a1) * r, math.sin(a1) * r))
            seg = p1 - p0
            sag = 0.9 + 0.1 * rnd.random()
            p = hg.box("%s_R%d_%d" % (name, ring, i), (0.002, seg.length * sag, 0.003), (p0 + p1) / 2 * sag, "Web", coll)
            p.rotation_euler.x = math.atan2(seg.z, seg.y)
            parts.append(p)
    return hg.join(parts, name)


def chained_door_dressing(name, coll):
    """Chains crossing the door, the three chain padlocks and the big green lock under a web.
    Pivot at the hinge like the door; everything sits 6 cm in front of the -X face of the leaf."""
    w = DOOR_W - 0.02
    x = -0.06
    parts = []
    for i, (a, b) in enumerate((((x, -0.1, 1.9), (x, w + 0.1, 1.45)), ((x, -0.1, 1.35), (x, w + 0.1, 1.8)), ((x, -0.1, 0.75), (x, w + 0.1, 0.95)))):
        parts += chain("%s_Chain%d" % (name, i), a, b, coll)
    # Wall staples the chains are bolted to.
    for i, (y, z) in enumerate(((-0.1, 1.9), (w + 0.1, 1.45), (-0.1, 1.35), (w + 0.1, 1.8), (-0.1, 0.75), (w + 0.1, 0.95))):
        parts.append(hg.box("%s_Staple%d" % (name, i), (0.04, 0.05, 0.08), (x + 0.02, y, z), "MetalRust", coll, bevel=0.008))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    hg.mirror_y(obj)  # matches the mirrored door leaf
    return obj


def coat_rack(name, coll):
    parts = [hg.cylinder(name + "_Pole", 0.022, 1.75, (0, 0, 0.9), "WoodDark", coll, segments=12)]
    for i in range(3):
        a = 2 * math.pi * i / 3
        leg = hg.box("%s_Leg%d" % (name, i), (0.32, 0.035, 0.035), (math.cos(a) * 0.14, math.sin(a) * 0.14, 0.06), "WoodDark", coll, bevel=0.01)
        leg.rotation_euler = (0, math.radians(-14), a)
        parts.append(leg)
    for i in range(6):
        a = 2 * math.pi * i / 6
        hook = hg.cylinder("%s_Hook%d" % (name, i), 0.01, 0.2, (math.cos(a) * 0.08, math.sin(a) * 0.08, 1.62), "WoodDark", coll, segments=8)
        hook.rotation_euler = (math.cos(a + math.pi / 2) * math.radians(55), math.sin(a + math.pi / 2) * -math.radians(55), 0)
        hook.rotation_euler = (0, math.radians(55), a)
        parts.append(hook)
        parts.append(hg.sphere("%s_HookEnd%d" % (name, i), 0.016, (math.cos(a) * 0.16, math.sin(a) * 0.16, 1.68), "WoodDark", coll, segments=8, rings=4))
    parts.append(hg.sphere(name + "_Top", 0.04, (0, 0, 1.8), "WoodDark", coll, segments=12, rings=6))
    # A long coat hanging on one hook: narrow shoulders, wider hem, a collar.
    shoulders = hg.box(name + "_CoatTop", (0.14, 0.34, 0.25), (0.19, 0, 1.47), "Fabric", coll, bevel=0.05)
    body = hg.cylinder(name + "_CoatBody", 0.2, 0.75, (0.19, 0, 1.0), "Fabric", coll, segments=10, radius_top=0.16)
    body.scale = (0.45, 1.0, 1.0)
    collar = hg.box(name + "_Collar", (0.09, 0.18, 0.08), (0.17, 0, 1.6), "Fabric", coll, bevel=0.03)
    for p in (shoulders, body, collar):
        hg.jitter(p, 0.012, seed=2)
    parts += [shoulders, body, collar]
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def phone_table(name, coll):
    """Small side table with two drawers, cabriole-ish legs."""
    top = 0.78
    parts = [hg.box(name + "_Top", (0.42, 0.62, 0.035), (0, 0, top), "WoodPainted", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Body", (0.36, 0.56, 0.22), (0, 0, top - 0.13), "WoodPainted", coll, bevel=0.008))
    for i, z in enumerate((top - 0.08, top - 0.19)):
        parts.append(hg.box("%s_Drawer%d" % (name, i), (0.01, 0.48, 0.085), (-0.185, 0, z), "WoodDark", coll, bevel=0.004))
        parts.append(hg.sphere("%s_Pull%d" % (name, i), 0.012, (-0.2, 0, z), "Brass", coll, segments=8, rings=4))
    for i, (x, y) in enumerate(((-0.15, -0.25), (-0.15, 0.25), (0.15, -0.25), (0.15, 0.25))):
        leg = hg.cylinder("%s_Leg%d" % (name, i), 0.022, top - 0.24, (x, y, (top - 0.24) / 2), "WoodPainted", coll, segments=10, radius_top=0.03)
        leg.rotation_euler.y = math.radians(-4 if x < 0 else 4)
        parts.append(leg)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def rotary_phone(name, coll):
    """Bakelite desk phone with a dial and the handset on the cradle. Pivot on the bottom."""
    parts = [hg.box(name + "_Base", (0.2, 0.22, 0.08), (0, 0, 0.04), "Bakelite", coll, bevel=0.025)]
    front = hg.box(name + "_Front", (0.1, 0.2, 0.05), (-0.06, 0, 0.085), "Bakelite", coll, bevel=0.02)
    front.rotation_euler.y = math.radians(25)
    parts.append(front)
    parts.append(hg.cylinder(name + "_Dial", 0.055, 0.012, (-0.085, 0, 0.11), "MetalDark", coll, segments=20, rotation=(0, math.radians(-65), 0)))
    parts.append(hg.cylinder(name + "_DialCenter", 0.02, 0.016, (-0.087, 0, 0.112), "Trim", coll, segments=12, rotation=(0, math.radians(-65), 0)))
    handle = hg.cylinder(name + "_Handle", 0.017, 0.2, (0.03, 0, 0.13), "Bakelite", coll, segments=10, rotation=(math.radians(90), 0, 0))
    parts.append(handle)
    for side in (-1, 1):
        parts.append(hg.box("%s_Cup%d" % (name, side), (0.06, 0.06, 0.04), (0.03, side * 0.1, 0.12), "Bakelite", coll, bevel=0.018))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def wall_sconce(name, coll):
    """Wall lamp: back plate, curved arm, tulip shade. Pivot at the wall (Y=0), shade towards -Y."""
    parts = [hg.box(name + "_Plate", (0.08, 0.015, 0.14), (0, -0.008, 0), "Brass", coll, bevel=0.01)]
    arm = hg.cylinder(name + "_Arm", 0.008, 0.16, (0, -0.07, 0.03), "Brass", coll, segments=8, rotation=(math.radians(70), 0, 0))
    parts.append(arm)
    parts.append(hg.cylinder(name + "_Shade", 0.035, 0.11, (0, -0.15, 0.12), "LampShade", coll, segments=14, radius_top=0.065))
    parts.append(hg.sphere(name + "_Bulb", 0.025, (0, -0.15, 0.1), "LampShade", coll, segments=10, rings=6))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def photo_frame(name, coll, width=0.36, height=0.46):
    """Frame with a picture plane (material M_Picture: Unreal swaps in the photo). Hangs on the wall: back at Y=0."""
    t = 0.04
    parts = []
    for i, (w, h, x, z) in enumerate(((width, t, 0, height / 2 - t / 2), (width, t, 0, -height / 2 + t / 2),
                                      (t, height, -width / 2 + t / 2, 0), (t, height, width / 2 - t / 2, 0))):
        parts.append(hg.box("%s_F%d" % (name, i), (w, 0.03, h), (x, -0.015, z), "WoodDark", coll, bevel=0.006))
    pic = hg.plane(name + "_Pic", (width - 2 * t, height - 2 * t), (0, -0.012, 0), "Picture", coll)
    parts.append(pic)
    obj = hg.join(parts, name)
    return obj


def rug(name, coll, size=(1.4, 0.8), seed=4):
    parts = [hg.box(name + "_Mat", (size[0], size[1], 0.012), (0, 0, 0.006), "Rug", coll, bevel=0.004)]
    hg.jitter(parts[0], 0.004, seed=seed)
    # Fringe at both ends.
    for end in (-1, 1):
        for i in range(int(size[1] / 0.04)):
            parts.append(hg.box("%s_Fr%d_%d" % (name, end, i), (0.04, 0.006, 0.003), (end * (size[0] / 2 + 0.02), -size[1] / 2 + 0.02 + i * 0.04, 0.003), "Trim", coll))
    obj = hg.join(parts, name)
    # One runner picture over the whole rug, the border follows its edges.
    hg.planar_uv(obj)
    return obj


# --- Build and export ------------------------------------------------------------------------------

def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Hallway")
    assets = [
        wall_module("SM_Wall_100", 1.0, coll),
        wall_module("SM_Wall_50", 0.5, coll),
        wall_module("SM_Wall_200", 2.0, coll),
        door_wall_module("SM_Wall_Door_160", 1.6, coll),
        window_wall_module("SM_Wall_WindowNarrow_100", 1.0, coll),
        ceiling_lamp("SM_CeilingLamp", coll),
        floor_planks("SM_Floor_Planks_100", coll),
        ceiling("SM_Ceiling_100", coll),
        door_panel("SM_Door_Panel", coll),
        chained_door_dressing("SM_ChainedDoor_Chains", coll),
        padlock("SM_Padlock", coll, "PaintRed", size=1.6),
        padlock("SM_Padlock_Big", coll, "PaintGreen", size=2.6),
        spider_web("SM_SpiderWeb", coll),
        coat_rack("SM_CoatRack", coll),
        phone_table("SM_PhoneTable", coll),
        rotary_phone("SM_RotaryPhone", coll),
        wall_sconce("SM_WallSconce", coll),
        photo_frame("SM_PhotoFrame", coll),
        rug("SM_Rug_Runner", coll),
    ]
    exported = []
    for obj in assets:
        exported.append(hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx")))

    # Lay the pieces out in a row so they can be reviewed side by side.
    x = 0.0
    for obj in assets:
        dims = obj.dimensions
        obj.location.x = x + dims.x / 2 if obj.name.startswith("SM_Wall") is False else x
        x += max(dims.x, 0.6) + 0.5
    hg.save_blend(os.path.join(OUT, "Hallway_Kit.blend"))
    print("exported %d assets to %s" % (len(exported), OUT))


build()
