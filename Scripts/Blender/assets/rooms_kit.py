"""
Upstairs rooms and stairs (Apple_Room, Upstair_Hall, Safe_Room, Bulb_room concepts): gilded picture
frames, painted wardrobe, wooden bed, nightstand, stairs with banister, wall shelf, old TV, lamp socket
with loose wires, light bulb, flashlight, caution tape cross, blood trail decal, small cabriole desk.
"""

import importlib
import math
import os
import random
import sys

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Rooms")


def gilded_frame(name, coll, width, height, depth=0.05, border=0.07):
    """Picture frame with a bevelled moulding and a canvas plane (M_Painting, swapped per instance).
    Hangs on a wall: back at Y=0, canvas facing -Y (Blender) = +Y (Unreal)."""
    parts = []
    for i, (w, h, x, z) in enumerate(((width, border, 0, height / 2 - border / 2), (width, border, 0, -height / 2 + border / 2),
                                      (border, height, -width / 2 + border / 2, 0), (border, height, width / 2 - border / 2, 0))):
        parts.append(hg.box("%s_F%d" % (name, i), (w, depth, h), (x, -depth / 2, z), "Gilt", coll, bevel=0.015))
        inner = hg.box("%s_I%d" % (name, i), (w if w > border else border * 0.4, depth * 0.4, h if h > border else border * 0.4), (0, 0, 0), "GiltDark", coll)
        inner.dimensions = (max(w - 2 * border, border * 0.35) if w > border else border * 0.35, depth * 0.4, max(h - 2 * border, border * 0.35) if h > border else border * 0.35)
        inner.location = (x * (1 - border / width * 1.5) if abs(x) > 0 else 0, -depth - 0.002, z * (1 - border / height * 1.5) if abs(z) > 0 else 0)
        parts.append(inner)
    parts.append(hg.plane(name + "_Canvas", (width - 2 * border, height - 2 * border), (0, -depth * 0.55, 0), "Painting", coll))
    obj = hg.join(parts, name)
    return obj


def wardrobe(name, coll, size=(0.6, 1.1, 1.95)):
    """Painted wardrobe with chipped paint (Apple_Room): two panelled doors, cornice, knobs, feet."""
    d, w, h = size
    parts = [hg.box(name + "_Body", (d, w, h - 0.12), (0, 0, (h - 0.12) / 2 + 0.1), "WoodPaintedRed", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Cornice", (d + 0.08, w + 0.1, 0.1), (-0.02, 0, h + 0.03), "WoodPaintedRed", coll, bevel=0.02))
    parts.append(hg.box(name + "_Plinth", (d + 0.04, w + 0.04, 0.08), (0, 0, 0.12), "WoodPaintedRed", coll, bevel=0.01))
    for i, sgn in enumerate((-1, 1)):
        yc = sgn * w / 4
        parts.append(hg.box("%s_Door%d" % (name, i), (0.02, w / 2 - 0.04, h - 0.3), (-d / 2 - 0.008, yc, h / 2 + 0.03), "WoodPaintedRed", coll, bevel=0.006))
        for k, (z0, z1) in enumerate(((0.3, 0.95), (1.05, h - 0.2))):
            parts.append(hg.box("%s_Pan%d%d" % (name, i, k), (0.012, w / 2 - 0.16, z1 - z0), (-d / 2 - 0.02, yc, (z0 + z1) / 2), "WoodPaintedRedDark", coll, bevel=0.006))
        parts.append(hg.sphere("%s_Knob%d" % (name, i), 0.022, (-d / 2 - 0.04, sgn * 0.05, h / 2), "Brass", coll, segments=10, rings=5))
    for i, (x, y) in enumerate(((-d / 2 + 0.06, -w / 2 + 0.06), (-d / 2 + 0.06, w / 2 - 0.06), (d / 2 - 0.06, -w / 2 + 0.06), (d / 2 - 0.06, w / 2 - 0.06))):
        parts.append(hg.cylinder("%s_Foot%d" % (name, i), 0.035, 0.08, (x, y, 0.04), "WoodPaintedRed", coll, segments=8, radius_top=0.025))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def bed(name, coll, size=(2.0, 0.95)):
    """Single wooden bed (Apple_Room, Player_Room): headboard with posts and ball finials, mattress,
    rumpled blanket, pillow. Head at +X."""
    l, w = size
    parts = []
    for end, (x, ph) in enumerate(((l / 2, 1.05), (-l / 2, 0.75))):
        parts.append(hg.box("%s_Board%d" % (name, end), (0.05, w, ph - 0.25), (x, 0, 0.25 + (ph - 0.25) / 2), "WoodDark", coll, bevel=0.01))
        for k, y in enumerate((-w / 2, w / 2)):
            parts.append(hg.cylinder("%s_Post%d%d" % (name, end, k), 0.04, ph, (x, y, ph / 2), "WoodDark", coll, segments=10))
            parts.append(hg.sphere("%s_Ball%d%d" % (name, end, k), 0.06, (x, y, ph + 0.05), "WoodDark", coll, segments=12, rings=6))
    for k, y in enumerate((-w / 2, w / 2)):
        parts.append(hg.box("%s_Rail%d" % (name, k), (l, 0.04, 0.16), (0, y, 0.3), "WoodDark", coll, bevel=0.008))
    mattress = hg.box(name + "_Mattress", (l - 0.08, w - 0.06, 0.2), (0, 0, 0.44), "Fabric_Light", coll, bevel=0.05)
    blanket = hg.box(name + "_Blanket", (l * 0.7, w + 0.04, 0.06), (-l * 0.12, 0, 0.56), "Blanket", coll, bevel=0.03)
    hg.jitter(blanket, 0.03, seed=7)
    pillow = hg.box(name + "_Pillow", (0.4, w * 0.75, 0.13), (l / 2 - 0.3, 0, 0.6), "Fabric_Light", coll, bevel=0.06)
    hg.jitter(pillow, 0.015, seed=8)
    parts += [mattress, blanket, pillow]
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def nightstand(name, coll):
    parts = [hg.box(name + "_Top", (0.42, 0.45, 0.04), (0, 0, 0.6), "WoodDark", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Body", (0.38, 0.41, 0.2), (0, 0, 0.47), "WoodDark", coll, bevel=0.008))
    parts.append(hg.box(name + "_Drawer", (0.012, 0.35, 0.14), (-0.195, 0, 0.47), "WoodPanel", coll, bevel=0.004))
    parts.append(hg.sphere(name + "_Pull", 0.015, (-0.21, 0, 0.47), "Brass", coll, segments=8, rings=4))
    parts.append(hg.box(name + "_Shelf", (0.36, 0.39, 0.02), (0, 0, 0.15), "WoodDark", coll))
    for i, (x, y) in enumerate(((-0.17, -0.18), (-0.17, 0.18), (0.17, -0.18), (0.17, 0.18))):
        parts.append(hg.box("%s_Leg%d" % (name, i), (0.04, 0.04, 0.6), (x, y, 0.3), "WoodDark", coll, bevel=0.006))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def staircase(name, coll, rise=3.0, run=4.8, width=1.6, steps=15):
    """Straight wooden stairs with a banister on the open side (-Y), newel posts and balusters
    (Upstair_Hall, Hallway_02). Pivot: bottom front corner on the open side; climbs along +X."""
    parts = []
    h = rise / steps
    d = run / steps
    for i in range(steps):
        x0 = i * d
        z = (i + 1) * h
        parts.append(hg.box("%s_Tread%d" % (name, i), (d + 0.03, width, 0.04), (x0 + d / 2, width / 2, z - 0.02), "WoodFloor", coll, bevel=0.008))
        parts.append(hg.box("%s_Riser%d" % (name, i), (0.025, width, h - 0.04), (x0 + 0.012, width / 2, z - h / 2 - 0.02), "WoodDark", coll))
    # Stringers and the solid underside.
    angle = math.atan2(rise, run)
    length = math.hypot(rise, run)
    for k, y in enumerate((0.0, width)):
        s = hg.box("%s_Stringer%d" % (name, k), (length + 0.2, 0.05, 0.3), (run / 2, y, rise / 2 - 0.05), "WoodDark", coll, bevel=0.01)
        s.rotation_euler.y = -angle
        parts.append(s)
    # Banister on the open side: newels, a handrail and turned balusters on each tread.
    rail_h = 0.9
    parts.append(hg.box(name + "_NewelLow", (0.12, 0.12, 1.15), (0.1, 0.0, 0.575 + h), "WoodDark", coll, bevel=0.015))
    parts.append(hg.sphere(name + "_NewelCap", 0.08, (0.1, 0.0, 1.2 + h), "WoodDark", coll, segments=12, rings=6))
    parts.append(hg.box(name + "_NewelTop", (0.1, 0.1, 1.0), (run - 0.05, 0.0, rise + 0.5), "WoodDark", coll, bevel=0.012))
    parts.append(hg.rod(name + "_Handrail", (0.1, 0.0, h + rail_h + 0.1), (run - 0.05, 0.0, rise + rail_h), 0.035, "WoodDark", coll))
    for i in range(1, steps):
        x = i * d + d / 2
        z0 = (i + 1) * h
        z1 = h + rail_h + 0.1 + (x - 0.1) / (run - 0.15) * (rise - h - 0.1)
        bal = hg.cylinder("%s_Bal%d" % (name, i), 0.022, z1 - z0, (x, 0.0, (z0 + z1) / 2), "WoodDark", coll, segments=8)
        parts.append(bal)
        parts.append(hg.sphere("%s_BalBulb%d" % (name, i), 0.03, (x, 0.0, z0 + 0.15), "WoodDark", coll, segments=8, rings=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def wall_shelf(name, coll, length=0.9):
    """Plank shelf on two curved brackets (Bulb_room, Player_Room). Back at Y=0, sticks out to -Y."""
    parts = [hg.box(name + "_Board", (length, 0.24, 0.03), (0, -0.12, 0.0), "WoodWorn", coll, bevel=0.006)]
    for i, x in enumerate((-length / 2 + 0.1, length / 2 - 0.1)):
        parts.append(hg.box("%s_BrV%d" % (name, i), (0.03, 0.03, 0.2), (x, -0.015, -0.11), "WoodDark", coll))
        br = hg.box("%s_BrD%d" % (name, i), (0.03, 0.25, 0.03), (x, -0.1, -0.11), "WoodDark", coll)
        br.rotation_euler.x = math.radians(-40)
        parts.append(br)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def old_tv(name, coll):
    """Wooden-cabinet CRT television with a rounded screen and two knobs (Bulb_room). Screen faces -X."""
    parts = [hg.box(name + "_Cabinet", (0.45, 0.6, 0.48), (0, 0, 0.24), "WoodDark", coll, bevel=0.03)]
    parts.append(hg.box(name + "_Bezel", (0.02, 0.42, 0.36), (-0.225, -0.05, 0.25), "Bakelite", coll, bevel=0.04))
    screen = hg.sphere(name + "_Screen", 0.2, (-0.22, -0.05, 0.25), "Screen", coll, segments=16, rings=8, scale=(0.18, 0.95, 0.8))
    parts.append(screen)
    for i, z in enumerate((0.32, 0.2)):
        parts.append(hg.cylinder("%s_Knob%d" % (name, i), 0.025, 0.03, (-0.235, 0.22, z), "Bakelite", coll, segments=10, rotation=(0, math.radians(90), 0)))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def lamp_socket(name, coll, with_bulb=False):
    """Round porcelain wall socket with loose wires hanging out (Bulb_room). Back at Y=0, faces -Y."""
    parts = [hg.cylinder(name + "_Plate", 0.08, 0.02, (0, -0.01, 0), "Porcelain", coll, segments=20, rotation=(math.radians(90), 0, 0))]
    parts.append(hg.cylinder(name + "_Holder", 0.035, 0.07, (0, -0.055, 0), "Porcelain", coll, segments=14, rotation=(math.radians(90), 0, 0)))
    rnd = random.Random(4)
    for i in range(3):
        p0 = (0.01 * (i - 1), -0.06, -0.02)
        p1 = (0.04 * (i - 1) + rnd.uniform(-0.02, 0.02), -0.05, -0.16 - rnd.uniform(0, 0.06))
        p2 = (p1[0] + rnd.uniform(-0.03, 0.03), -0.04, p1[2] - 0.06)
        parts.append(hg.rod("%s_WireA%d" % (name, i), p0, p1, 0.004, "MetalDark", coll, segments=6))
        parts.append(hg.rod("%s_WireB%d" % (name, i), p1, p2, 0.004, "MetalDark", coll, segments=6))
    if with_bulb:
        parts += bulb_parts(name + "_B", coll, (0, -0.09, 0), horizontal=True)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def bulb_parts(name, coll, base=(0, 0, 0), horizontal=False):
    """Incandescent bulb: glass pear and a ribbed brass screw base."""
    bx, by, bz = base
    if horizontal:
        glass = hg.sphere(name + "_Glass", 0.04, (bx, by - 0.07, bz), "BulbGlass", coll, segments=14, rings=8, scale=(1, 1.3, 1))
        parts = [glass]
        for k in range(3):
            parts.append(hg.cylinder("%s_Screw%d" % (name, k), 0.016, 0.01, (bx, by - 0.005 - k * 0.012, bz), "Brass", coll, segments=10, rotation=(math.radians(90), 0, 0)))
        return parts
    parts = [hg.sphere(name + "_Glass", 0.04, (bx, by, bz + 0.085), "BulbGlass", coll, segments=14, rings=8, scale=(1, 1, 1.3))]
    for k in range(3):
        parts.append(hg.cylinder("%s_Screw%d" % (name, k), 0.016, 0.01, (bx, by, bz + 0.008 + k * 0.012), "Brass", coll, segments=10))
    return parts


def bulb(name, coll):
    obj = hg.join(bulb_parts(name, coll), name)
    hg.world_uv(obj, scale=4.0)
    return obj


def flashlight(name, coll):
    """Rubber flashlight lying on its side (Bulb_room)."""
    parts = [hg.cylinder(name + "_Body", 0.025, 0.2, (0, 0, 0.025), "Bakelite", coll, segments=12, rotation=(0, math.radians(90), 0))]
    parts.append(hg.cylinder(name + "_Head", 0.045, 0.07, (0.13, 0, 0.045), "Bakelite", coll, segments=14, rotation=(0, math.radians(90), 0), radius_top=0.03))
    parts.append(hg.cylinder(name + "_Lens", 0.04, 0.005, (0.166, 0, 0.045), "BulbGlass", coll, segments=14, rotation=(0, math.radians(90), 0)))
    parts.append(hg.box(name + "_Switch", (0.03, 0.015, 0.01), (0.0, 0, 0.052), "MetalDark", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def caution_tape(name, coll, width=1.3, height=1.5):
    """Two crossed strips of police tape across a doorway (Safe_Room). Plane in the XZ plane at Y=0."""
    parts = []
    for i, ang in enumerate((-22, 20)):
        strip = hg.plane("%s_S%d" % (name, i), (width * 1.15, 0.075), (0, -0.01 * i, height * (0.55 + 0.05 * i)), "CautionTape", coll)
        strip.rotation_euler.y = math.radians(ang)
        parts.append(strip)
    lower = hg.plane(name + "_S2", (width * 1.1, 0.075), (0, -0.02, height * 0.35), "CautionTape", coll)
    lower.rotation_euler.y = math.radians(-6)
    parts.append(lower)
    obj = hg.join(parts, name)
    return obj


def blood_trail(name, coll, length=2.5, width=0.6):
    """Decal plane on the floor (masked), long side along X."""
    obj = hg.plane(name, (length, width), (0, 0, 0.004), "BloodTrail", coll, rotation=(math.radians(-90), 0, 0))
    hg.apply_transforms(obj)
    return obj


def cabriole_desk(name, coll):
    """Small writing table with three drawers and curved legs (Safe_Room, left)."""
    parts = [hg.box(name + "_Top", (0.55, 1.15, 0.04), (0, 0, 0.78), "WoodWorn", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Apron", (0.5, 1.08, 0.14), (0, 0, 0.69), "WoodWorn", coll, bevel=0.008))
    for i, y in enumerate((-0.36, 0, 0.36)):
        parts.append(hg.box("%s_Dr%d" % (name, i), (0.012, 0.32, 0.1), (-0.255, y, 0.69), "WoodDark", coll, bevel=0.004))
        parts.append(hg.sphere("%s_Pull%d" % (name, i), 0.014, (-0.27, y, 0.69), "WoodDark", coll, segments=8, rings=4))
    for i, (x, y) in enumerate(((-0.22, -0.5), (-0.22, 0.5), (0.22, -0.5), (0.22, 0.5))):
        knee = (x, y, 0.62)
        mid = (x * 1.25, y * 1.04, 0.32)
        foot = (x * 1.05, y, 0.02)
        parts.append(hg.rod("%s_LegA%d" % (name, i), knee, mid, 0.03, "WoodWorn", coll))
        parts.append(hg.rod("%s_LegB%d" % (name, i), mid, foot, 0.022, "WoodWorn", coll))
        parts.append(hg.sphere("%s_Foot%d" % (name, i), 0.03, foot, "WoodWorn", coll, segments=8, rings=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Rooms")
    assets = [
        gilded_frame("SM_Frame_Gilt_Small", coll, 0.45, 0.55),
        gilded_frame("SM_Frame_Gilt_Medium", coll, 0.6, 0.75),
        gilded_frame("SM_Frame_Gilt_Large", coll, 0.85, 0.85),
        gilded_frame("SM_Frame_Portrait", coll, 0.75, 1.05),
        wardrobe("SM_Wardrobe_Red", coll),
        bed("SM_Bed_Single", coll),
        nightstand("SM_Nightstand", coll),
        staircase("SM_Staircase_15", coll),
        wall_shelf("SM_WallShelf", coll),
        old_tv("SM_TV_Old", coll),
        lamp_socket("SM_LampSocket", coll),
        lamp_socket("SM_LampSocket_Bulb", coll, with_bulb=True),
        bulb("SM_Bulb", coll),
        flashlight("SM_Flashlight", coll),
        caution_tape("SM_CautionTape_Cross", coll),
        blood_trail("SM_BloodTrail", coll),
        cabriole_desk("SM_Desk_Cabriole", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.5) + 0.6
    hg.save_blend(os.path.join(OUT, "Rooms_Kit.blend"))
    print("exported %d room assets to %s" % (len(assets), OUT))


build()
