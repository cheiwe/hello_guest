"""
Common props used all over the house (concepts Workshop_with_crowds, Bulb_room, Basement_Fusebox,
Attic_Radio, Secret_Basement): cardboard boxes, wooden crates, paint cans, metal shelving, workbench,
desk lamp, metal locker, crowbar.

Exports to SourceArt/Models/Props/<name>.fbx. Pivot: centre of the footprint on the floor, front = -X
(in Unreal also -X: the mirror only flips Y).
"""

import importlib
import math
import os
import random
import sys

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Props")


def cardboard_box(name, coll, size=(0.5, 0.4, 0.35), open_flaps=False, seed=1):
    """Cardboard box with tape and slightly bulging sides; open boxes have flaps folded out."""
    rnd = random.Random(seed)
    w, d, h = size
    parts = []
    if open_flaps:
        # Hollow: four walls and a bottom so things can sit inside.
        t = 0.008
        parts.append(hg.box(name + "_Bottom", (w, d, t), (0, 0, t / 2), "Cardboard", coll))
        for i, (sx, sy, px, py) in enumerate(((w, t, 0, -d / 2), (w, t, 0, d / 2), (t, d, -w / 2, 0), (t, d, w / 2, 0))):
            parts.append(hg.box("%s_Side%d" % (name, i), (sx, sy, h), (px, py, h / 2), "Cardboard", coll))
        for i, (px, py, rx, ry, fw, fd) in enumerate(((0, -d / 2, -1, 0, w, d / 2), (0, d / 2, 1, 0, w, d / 2),
                                                       (-w / 2, 0, 0, -1, w / 2, d), (w / 2, 0, 0, 1, w / 2, d))):
            flap = hg.box("%s_Flap%d" % (name, i), (fw if rx else fw, fd if rx else fd, t), (0, 0, 0), "Cardboard", coll)
            if rx:
                flap.dimensions = (w * 0.98, d * 0.45, t)
                flap.location = (0, py + rx * d * 0.2, h + d * 0.12)
                flap.rotation_euler.x = math.radians(rx * rnd.uniform(110, 140))
            else:
                flap.dimensions = (w * 0.45, d * 0.98, t)
                flap.location = (px + ry * w * 0.2, 0, h + w * 0.12)
                flap.rotation_euler.y = math.radians(-ry * rnd.uniform(110, 140))
            parts.append(flap)
    else:
        body = hg.box(name + "_Body", size, (0, 0, h / 2), "Cardboard", coll, bevel=0.01)
        hg.jitter(body, 0.006, seed=seed)
        parts.append(body)
        parts.append(hg.box(name + "_Tape", (w + 0.004, 0.06, 0.004), (0, 0, h + 0.001), "Tape", coll))
        parts.append(hg.box(name + "_TapeF", (0.004, 0.06, 0.12), (-w / 2 - 0.001, 0, h - 0.06), "Tape", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def wooden_crate(name, coll, size=(0.6, 0.45, 0.4)):
    """Slatted crate with corner posts."""
    w, d, h = size
    parts = []
    slats = 3
    for side, (sx, sy, px, py) in enumerate(((w, 0.02, 0, -d / 2), (w, 0.02, 0, d / 2), (0.02, d, -w / 2, 0), (0.02, d, w / 2, 0))):
        for i in range(slats):
            z = h * (i + 0.5) / slats
            parts.append(hg.box("%s_S%d_%d" % (name, side, i), (sx, sy, h / slats - 0.03), (px, py, z), "WoodCrate", coll, bevel=0.004))
    for i, (px, py) in enumerate(((-w / 2, -d / 2), (w / 2, -d / 2), (-w / 2, d / 2), (w / 2, d / 2))):
        parts.append(hg.box("%s_Post%d" % (name, i), (0.04, 0.04, h), (px, py, h / 2), "WoodCrate", coll, bevel=0.005))
    parts.append(hg.box(name + "_Bottom", (w, d, 0.02), (0, 0, 0.01), "WoodCrate", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def paint_can(name, coll, radius=0.09, height=0.2, drips=True, seed=2):
    """Paint can with rim, wire handle and drips of paint down the side."""
    rnd = random.Random(seed)
    parts = [hg.cylinder(name + "_Body", radius, height, (0, 0, height / 2), "MetalCan", coll, segments=20)]
    parts.append(hg.cylinder(name + "_Rim", radius + 0.004, 0.012, (0, 0, height - 0.006), "MetalCan", coll, segments=20))
    parts.append(hg.cylinder(name + "_Lid", radius - 0.006, 0.006, (0, 0, height + 0.002), "Paint", coll, segments=20))
    parts.append(hg.cylinder(name + "_Label", radius + 0.002, height * 0.5, (0, 0, height * 0.45), "Label", coll, segments=20))
    handle = hg.torus(name + "_Handle", radius, 0.004, (0, 0, height), "MetalDark", coll, rotation=(math.radians(90), 0, 0), scale=(1, 1, 0.9))
    parts.append(handle)
    if drips:
        for i in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            length = rnd.uniform(0.04, 0.12)
            parts.append(hg.box("%s_Drip%d" % (name, i), (0.006, 0.02, length), (math.cos(a) * (radius + 0.002), math.sin(a) * (radius + 0.002), height - length / 2), "Paint", coll, bevel=0.003))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def metal_shelving(name, coll, size=(1.2, 0.45, 1.9), shelves=4):
    """Grey metal shelving unit: angle posts and thin shelves (Workshop_with_crowds)."""
    w, d, h = size
    parts = []
    for i, (px, py) in enumerate(((-w / 2, -d / 2), (w / 2, -d / 2), (-w / 2, d / 2), (w / 2, d / 2))):
        parts.append(hg.box("%s_Post%d" % (name, i), (0.035, 0.035, h), (px, py, h / 2), "MetalPainted", coll))
    for i in range(shelves):
        z = 0.1 + i * (h - 0.15) / (shelves - 1)
        parts.append(hg.box("%s_Shelf%d" % (name, i), (w, d, 0.02), (0, 0, z), "MetalPainted", coll, bevel=0.004))
        parts.append(hg.box("%s_Lip%d" % (name, i), (w, 0.01, 0.04), (0, -d / 2, z - 0.01), "MetalPainted", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def workbench(name, coll, size=(1.5, 0.75, 0.85)):
    """Heavy wooden workbench with a lower shelf (the crowbar lies on it)."""
    w, d, h = size
    parts = []
    for i in range(4):
        y = -d / 2 + d * (i + 0.5) / 4
        board = hg.box("%s_Top%d" % (name, i), (w, d / 4 - 0.008, 0.05), (0, y, h - 0.025), "WoodWorn", coll, bevel=0.006)
        parts.append(board)
    for i, (px, py) in enumerate(((-w / 2 + 0.07, -d / 2 + 0.07), (w / 2 - 0.07, -d / 2 + 0.07), (-w / 2 + 0.07, d / 2 - 0.07), (w / 2 - 0.07, d / 2 - 0.07))):
        leg = hg.box("%s_Leg%d" % (name, i), (0.08, 0.08, h - 0.05), (px, py, (h - 0.05) / 2), "WoodWorn", coll, bevel=0.008)
        leg.rotation_euler.x = math.radians(2 if py > 0 else -2)
        parts.append(leg)
    parts.append(hg.box(name + "_Shelf", (w - 0.1, d - 0.1, 0.03), (0, 0, 0.2), "WoodWorn", coll, bevel=0.005))
    for i, py in enumerate((-d / 2 + 0.07, d / 2 - 0.07)):
        parts.append(hg.box("%s_Rail%d" % (name, i), (w - 0.14, 0.04, 0.08), (0, py, h - 0.1), "WoodWorn", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def desk_lamp(name, coll):
    """Articulated desk lamp with a metal cone shade (Workshop_with_crowds). Pivot under the base."""
    base_top = (0.0, 0.0, 0.035)
    elbow = (0.12, 0.0, 0.36)
    head = (-0.08, 0.0, 0.55)
    parts = [hg.cylinder(name + "_Base", 0.09, 0.03, (0, 0, 0.015), "MetalPainted", coll, segments=20, radius_top=0.075)]
    parts.append(hg.rod(name + "_Arm1", base_top, elbow, 0.009, "MetalDark", coll))
    parts.append(hg.rod(name + "_Arm2", elbow, head, 0.009, "MetalDark", coll))
    for i, p in enumerate((base_top, elbow, head)):
        parts.append(hg.sphere("%s_Joint%d" % (name, i), 0.017, p, "MetalDark", coll, segments=8, rings=4))
    # Cone shade hanging from the head joint, opening down and towards -X (the work surface).
    tip = (-0.2, 0.0, 0.43)
    parts.append(hg.rod(name + "_Neck", head, (-0.11, 0, 0.52), 0.012, "MetalDark", coll))
    shade = hg.cylinder(name + "_Shade", 0.035, 0.15, (0, 0, 0), "MetalPainted", coll, segments=16, radius_top=0.09)
    shade.rotation_mode = "QUATERNION"
    from mathutils import Vector as _V
    axis = (_V(tip) - _V((-0.11, 0, 0.52))).normalized()
    shade.rotation_quaternion = _V((0, 0, 1)).rotation_difference(axis)
    shade.location = (_V((-0.11, 0, 0.52)) + _V(tip)) / 2
    parts.append(shade)
    parts.append(hg.sphere(name + "_Bulb", 0.03, tip, "LampShade", coll, segments=10, rings=6))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def metal_locker(name, coll, size=(0.5, 0.5, 1.8)):
    """Old grey metal locker with vents and a handle."""
    w, d, h = size
    parts = [hg.box(name + "_Body", size, (0, 0, h / 2), "MetalPainted", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Door", (0.01, w - 0.06, h - 0.08), (-d / 2 - 0.004, 0, h / 2), "MetalPainted", coll, bevel=0.004))
    for i in range(3):
        parts.append(hg.box("%s_Vent%d" % (name, i), (0.006, w * 0.3, 0.015), (-d / 2 - 0.01, 0, h - 0.25 - i * 0.04), "MetalDark", coll))
    parts.append(hg.box(name + "_Handle", (0.03, 0.02, 0.14), (-d / 2 - 0.02, w / 2 - 0.08, h * 0.5), "MetalDark", coll, bevel=0.004))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def crowbar(name, coll, length=0.75):
    """Red crowbar (Crowbar concept): straight shaft, hooked claw at one end, flat chisel at the other."""
    r = 0.012
    parts = [hg.cylinder(name + "_Shaft", r, length, (0, 0, r), "PaintRed", coll, segments=8, rotation=(0, math.radians(90), 0))]
    # Hook: the shaft bends up and back along a 160 degree arc, built from short segments.
    bend = 0.05
    cx, cz = length / 2, r + bend
    steps = 8
    for i in range(steps):
        a0 = math.radians(-90 + 160 * i / steps)
        a1 = math.radians(-90 + 160 * (i + 1) / steps)
        x0, z0 = cx + math.cos(a0) * bend, cz + math.sin(a0) * bend
        x1, z1 = cx + math.cos(a1) * bend, cz + math.sin(a1) * bend
        seg = hg.cylinder("%s_Hook%d" % (name, i), r, math.hypot(x1 - x0, z1 - z0) + 0.004, ((x0 + x1) / 2, 0, (z0 + z1) / 2), "PaintRed", coll, segments=8)
        seg.rotation_euler.y = math.atan2(x1 - x0, z1 - z0)
        parts.append(seg)
    # Split claw at the tip of the hook.
    tip_a = math.radians(70)
    claw = hg.box(name + "_Claw", (0.012, 0.032, 0.035), (cx + math.cos(tip_a) * bend - 0.01, 0, cz + math.sin(tip_a) * bend + 0.01), "PaintRed", coll, bevel=0.004)
    claw.rotation_euler.y = math.radians(-40)
    parts.append(claw)
    chisel = hg.box(name + "_Chisel", (0.06, 0.03, 0.01), (-length / 2 - 0.02, 0, 0.008), "PaintRed", coll, bevel=0.003)
    chisel.rotation_euler.y = math.radians(-12)
    parts.append(chisel)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Props_Common")
    assets = [
        cardboard_box("SM_Box_Closed_A", coll, (0.5, 0.4, 0.35), seed=1),
        cardboard_box("SM_Box_Closed_B", coll, (0.4, 0.4, 0.3), seed=2),
        cardboard_box("SM_Box_Closed_Long", coll, (0.7, 0.35, 0.25), seed=3),
        cardboard_box("SM_Box_Open_A", coll, (0.5, 0.4, 0.3), open_flaps=True, seed=4),
        cardboard_box("SM_Box_Open_B", coll, (0.42, 0.36, 0.26), open_flaps=True, seed=5),
        wooden_crate("SM_Crate_Wood", coll),
        paint_can("SM_PaintCan_A", coll, seed=6),
        paint_can("SM_PaintCan_Tall", coll, radius=0.08, height=0.26, seed=7),
        metal_shelving("SM_Shelving_Metal", coll),
        workbench("SM_Workbench", coll),
        desk_lamp("SM_DeskLamp", coll),
        metal_locker("SM_Locker_Metal", coll),
        crowbar("SM_Crowbar", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.4) + 0.4
    hg.save_blend(os.path.join(OUT, "Props_Common.blend"))
    print("exported %d props to %s" % (len(assets), OUT))


build()
