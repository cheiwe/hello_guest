"""
Attic (Attic_Radio concept): the radio station with its puzzle parts (8 toggles, 3 beacons, red box
behind a chain-link grill), the boarded wardrobe, roof timber, skylights, the broken tower wall,
a plank table, a small dresser, cables, papers and an old transformer.

The radio station is wall equipment: back at Y=0, front to -Y (Blender) = +Y (Unreal). The moving
puzzle parts are separate meshes; where they sit on the console is written to RadioStation_sockets.json
(Blender metres and degrees) for the level script.
"""

import importlib
import json
import math
import os
import random
import sys

import bmesh
import bpy

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Attic")
SCREENS = ("ScreenTerminal", "ScreenWave", "ScreenAmber")

# Radio station layout (metres).
MAIN_X0, MAIN_X1 = -0.35, 1.15        # monitor panel
GRILL_X0, GRILL_X1 = -1.15, -0.35     # cabinet with the grill and the red box
FRONT = -0.55                         # front face of the monitor panel
DESK_TILT = math.degrees(math.atan2(0.16, 0.40))
DESK_CENTRE = (0.0, -0.75, 0.70)      # x is filled in per toggle


def profile_extrude(name, pts, depth, coll, mat, axis="x"):
    """Prism from a 2D outline (any shape, also concave) extruded along X (outline in YZ) or
    Y (outline in XZ), centred on the axis."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    def co(p, t):
        return (t, p[0], p[1]) if axis == "x" else (p[0], t, p[1])

    front = [bm.verts.new(co(p, -depth / 2)) for p in pts]
    back = [bm.verts.new(co(p, depth / 2)) for p in pts]
    caps = [bm.faces.new(front), bm.faces.new(list(reversed(back)))]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], back[i], back[j], front[j]))
    bmesh.ops.triangulate(bm, faces=caps)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material(mat))
    coll.objects.link(obj)
    return obj


# --- Radio station ---------------------------------------------------------------------------------

def gauge(name, coll, x, z, y, radius=0.065):
    """Round dial on a front panel: rim, cream face, needle."""
    rx = (math.radians(90), 0, 0)
    parts = [hg.cylinder(name + "_Rim", radius, 0.03, (x, y - 0.015, z), "ConsoleMetal", coll, segments=20, rotation=rx)]
    parts.append(hg.cylinder(name + "_Face", radius * 0.84, 0.01, (x, y - 0.026, z), "Gauge", coll, segments=20, rotation=rx))
    needle = hg.box(name + "_Needle", (0.004, 0.003, radius * 0.7), (x, y - 0.033, z + radius * 0.3), "MetalDark", coll)
    hg.rotate_about_z(needle, 0)
    needle.rotation_euler.y = math.radians(random.Random(name).uniform(-50, 50))
    parts.append(needle)
    parts.append(hg.cylinder(name + "_Pin", 0.008, 0.01, (x, y - 0.034, z), "MetalDark", coll, segments=8, rotation=rx))
    return parts


def monitor(name, coll, x, z, screen_mat):
    """Small CRT in a bevelled black housing set into the panel, curved glass screen."""
    parts = [hg.box(name + "_Housing", (0.33, 0.12, 0.28), (x, FRONT - 0.06, z), "Bakelite", coll, bevel=0.03)]
    parts.append(hg.box(name + "_Bezel", (0.28, 0.01, 0.23), (x, FRONT - 0.122, z), "MetalDark", coll, bevel=0.02))
    # Rounded-rectangle CRT glass, slightly domed: a heavily bevelled flat box.
    screen = hg.box(name + "_Screen", (0.25, 0.03, 0.2), (x, FRONT - 0.122, z), screen_mat, coll, bevel=0.012)
    for v in screen.data.vertices:
        if v.co.y < 0:
            v.co.y -= 0.012 * (1 - (v.co.x / 0.125) ** 2) * (1 - (v.co.z / 0.1) ** 2)
    hg.face_uv(screen, "xz")
    parts.append(screen)
    return parts


def radio_station(coll):
    rnd = random.Random(3)
    parts = []
    cx = (MAIN_X0 + MAIN_X1) / 2
    w = MAIN_X1 - MAIN_X0

    # Monitor panel body, its raised border and rivets.
    parts.append(hg.box("RS_Body", (w, -FRONT, 1.4), (cx, FRONT / 2, 1.3), "ConsoleMetal", coll, bevel=0.015))
    for i, (sx, sz, px, pz) in enumerate(((w, 0.05, cx, 1.975), (w, 0.05, cx, 0.625), (0.05, 1.4, MAIN_X0 + 0.025, 1.3), (0.05, 1.4, MAIN_X1 - 0.025, 1.3))):
        parts.append(hg.box("RS_Border%d" % i, (sx, 0.03, sz), (px, FRONT - 0.015, pz), "ConsoleMetal", coll, bevel=0.008))
    for i in range(8):
        x = MAIN_X0 + 0.08 + i * (w - 0.16) / 7
        for z in (1.975, 0.625):
            parts.append(hg.sphere("RS_RivH%d_%d" % (i, z * 100), 0.009, (x, FRONT - 0.03, z), "MetalDark", coll, segments=6, rings=3))

    # Top strip: three round gauges and a rectangular meter.
    for i, gx in enumerate((-0.12, 0.25, 0.62)):
        parts += gauge("RS_Gauge%d" % i, coll, gx, 1.8, FRONT)
    parts.append(hg.box("RS_MeterRim", (0.22, 0.03, 0.12), (0.97, FRONT - 0.015, 1.83), "ConsoleMetal", coll, bevel=0.01))
    parts.append(hg.box("RS_MeterFace", (0.19, 0.01, 0.09), (0.97, FRONT - 0.031, 1.83), "Gauge", coll))
    needle = hg.box("RS_MeterNeedle", (0.003, 0.003, 0.07), (0.95, FRONT - 0.037, 1.81), "MetalDark", coll)
    needle.rotation_euler.y = math.radians(25)
    parts.append(needle)

    # 2 x 4 monitors; vacuum tubes standing on the upper row.
    mats = (("ScreenAmber", "ScreenWave", "ScreenTerminal", "ScreenTerminal"),
            ("ScreenWave", "ScreenAmber", "ScreenTerminal", "ScreenAmber"))
    pitch = w / 4
    for row, z in enumerate((1.37, 1.04)):
        for k in range(4):
            x = MAIN_X0 + pitch / 2 + k * pitch
            parts += monitor("RS_Mon%d%d" % (row, k), coll, x, z, mats[row][k])
            if row == 0:
                for t, dx in enumerate((-0.07, 0.07)):
                    tz = z + 0.14
                    parts.append(hg.cylinder("RS_TubeBase%d%d" % (k, t), 0.026, 0.025, (x + dx, FRONT - 0.06, tz + 0.012), "MetalDark", coll, segments=10))
                    parts.append(hg.cylinder("RS_Tube%d%d" % (k, t), 0.021, 0.075, (x + dx, FRONT - 0.06, tz + 0.06), "TubeGlow", coll, segments=12))
                    parts.append(hg.sphere("RS_TubeTop%d%d" % (k, t), 0.021, (x + dx, FRONT - 0.06, tz + 0.098), "TubeGlow", coll, segments=12, rings=6))
            # Indicator LEDs under the lower row.
            if row == 1:
                for n in range(6):
                    led = rnd.choice(("LedRed", "LedGreen", "TubeGlow"))
                    parts.append(hg.box("RS_Led%d%d" % (k, n), (0.018, 0.012, 0.012), (x - 0.1 + n * 0.04, FRONT - 0.006, 0.83), led, coll, bevel=0.003))

    # Slanted control desk with slots for the eight toggles.
    tilt = math.radians(DESK_TILT)
    plate = hg.box("RS_Desk", (w + 0.05, 0.43, 0.04), (cx, DESK_CENTRE[1], DESK_CENTRE[2]), "ConsoleMetal", coll, bevel=0.01)
    plate.rotation_euler.x = tilt
    parts.append(plate)
    parts.append(hg.box("RS_DeskLip", (w + 0.05, 0.04, 0.08), (cx, -0.965, 0.6), "ConsoleMetal", coll, bevel=0.012))
    for i, x in enumerate((MAIN_X0 + 0.02, MAIN_X1 - 0.02)):
        parts.append(hg.box("RS_DeskCheek%d" % i, (0.04, 0.42, 0.62), (x, -0.76, 0.31), "ConsoleMetal", coll, bevel=0.008))
    sockets = []
    for i in range(8):
        x = cx - 0.665 + i * 0.19
        loc = (x, DESK_CENTRE[1] - 0.022 * math.sin(tilt), DESK_CENTRE[2] + 0.022 * math.cos(tilt))
        slot = hg.box("RS_Slot%d" % i, (0.075, 0.17, 0.012), loc, "MetalDark", coll, bevel=0.004)
        slot.rotation_euler.x = tilt
        parts.append(slot)
        sockets.append(dict(name="Toggle%d" % (i + 1), mesh="SM_Radio_Toggle", location=loc, rotation=(DESK_TILT, 0, 0)))
    # Lower cabinet under the desk: vent slats.
    parts.append(hg.box("RS_Lower", (w, -FRONT, 0.6), (cx, FRONT / 2, 0.3), "ConsoleMetal", coll))
    for i in range(7):
        parts.append(hg.box("RS_Vent%d" % i, (w * 0.6, 0.02, 0.018), (cx + 0.15, FRONT - 0.01, 0.12 + i * 0.045), "MetalDark", coll))

    # Side column with five big glowing bulbs (+X side).
    parts.append(hg.box("RS_Column", (0.08, 0.5, 1.5), (MAIN_X1 + 0.04, -0.27, 1.25), "ConsoleMetal", coll, bevel=0.01))
    ry = (0, math.radians(90), 0)
    for i, z in enumerate((1.8, 1.64, 1.48, 1.12, 0.96)):
        parts.append(hg.cylinder("RS_BulbHolder%d" % i, 0.035, 0.06, (MAIN_X1 + 0.11, -0.42, z), "Brass", coll, segments=12, rotation=ry))
        parts.append(hg.sphere("RS_Bulb%d" % i, 0.045, (MAIN_X1 + 0.19, -0.42, z), "TubeGlow", coll, segments=14, rings=8, scale=(1.6, 1, 1)))

    # Top: small radio set, beacon bases, two antennas.
    parts.append(hg.box("RS_Radio", (0.36, 0.3, 0.15), (0.0, -0.3, 2.075), "ConsoleMetal", coll, bevel=0.015))
    parts.append(hg.box("RS_RadioDial", (0.14, 0.01, 0.06), (-0.05, -0.455, 2.08), "Gauge", coll))
    for i, x in enumerate((0.07, 0.12)):
        parts.append(hg.cylinder("RS_RadioKnob%d" % i, 0.018, 0.02, (x, -0.46, 2.08), "Bakelite", coll, segments=10, rotation=(math.radians(90), 0, 0)))
    for i, x in enumerate((0.55, 0.8, 1.05)):
        sockets.append(dict(name="Beacon%d" % (i + 1), mesh="SM_Radio_Beacon", location=(x, -0.33, 2.0), rotation=(0, 0, 0)))
    for i, (base, top) in enumerate((((0.25, -0.12, 2.0), (0.12, -0.08, 2.8)), ((1.0, -0.1, 2.0), (1.28, -0.06, 2.72)))):
        parts.append(hg.rod("RS_Mast%d" % i, base, top, 0.012, "MetalDark", coll))
        for k in range(4):
            t = 0.45 + k * 0.17
            p = [base[j] + (top[j] - base[j]) * t for j in range(3)]
            half = 0.2 - k * 0.04
            bar = hg.rod("RS_Bar%d%d" % (i, k), (p[0] - half, p[1], p[2] + 0.02 * (k % 2)), (p[0] + half, p[1], p[2] - 0.02 * (k % 2)), 0.006, "MetalDark", coll, segments=6)
            hg.rotate_about_z(bar, 0)
            parts.append(bar)

    # Grill cabinet: open shell, lower panel with two gauges and a switch, mounting plate for the red box.
    gx = (GRILL_X0 + GRILL_X1) / 2
    gw = GRILL_X1 - GRILL_X0
    parts.append(hg.box("GC_Back", (gw, 0.04, 1.85), (gx, -0.02, 0.925), "ConsoleMetal", coll))
    parts.append(hg.box("GC_Top", (gw, 0.5, 0.04), (gx, -0.25, 1.83), "ConsoleMetal", coll, bevel=0.008))
    parts.append(hg.box("GC_Side", (0.04, 0.5, 1.85), (GRILL_X0 + 0.02, -0.25, 0.925), "ConsoleMetal", coll, bevel=0.008))
    parts.append(hg.box("GC_Lower", (gw, 0.5, 0.7), (gx, -0.25, 0.35), "ConsoleMetal", coll, bevel=0.01))
    for i, (sx, sz, px, pz) in enumerate(((gw, 0.06, gx, 1.78), (gw, 0.06, gx, 0.72), (0.06, 1.1, GRILL_X0 + 0.03, 1.25), (0.06, 1.1, GRILL_X1 - 0.03, 1.25))):
        parts.append(hg.box("GC_Frame%d" % i, (sx, 0.03, sz), (px, -0.485, pz), "ConsoleMetal", coll, bevel=0.008))
    for i, x in enumerate((gx - 0.18, gx + 0.02)):
        parts += gauge("GC_Gauge%d" % i, coll, x, 0.5, -0.5, radius=0.055)
    parts.append(hg.box("GC_SwitchPlate", (0.08, 0.02, 0.12), (gx + 0.22, -0.51, 0.5), "MetalDark", coll, bevel=0.005))
    parts.append(hg.box("GC_Switch", (0.03, 0.05, 0.06), (gx + 0.22, -0.54, 0.52), "BeaconRed", coll, bevel=0.008))
    parts.append(hg.box("GC_Mount", (0.5, 0.02, 0.95), (gx, -0.2, 1.25), "MetalDark", coll))
    sockets.append(dict(name="RedBox", mesh="SM_Radio_RedBox", location=(gx - 0.05, -0.21, 1.02), rotation=(0, 0, 0)))
    sockets.append(dict(name="RedBoxDoor", mesh="SM_Radio_RedBoxDoor", location=(gx - 0.05 - 0.13, -0.21 - 0.14, 1.02), rotation=(0, 0, 0)))
    sockets.append(dict(name="GrillDoor", mesh="SM_Radio_GrillDoor", location=(GRILL_X0 + 0.06, -0.49, 0.75), rotation=(0, 0, 0)))

    # Cables: red box to the panel, and a bundle out of the bottom onto the floor.
    for i in range(3):
        y = -0.25 - i * 0.03
        parts.append(hg.cable("RS_BoxCable%d" % i, [(gx + 0.08, y, 1.2 - i * 0.05), (gx + 0.2, y, 1.0 - i * 0.04), (GRILL_X1 - 0.02, y, 0.95 - i * 0.03)],
                              0.009, ("CableRed", "Cable", "CableGreen")[i], coll))
    for i in range(5):
        x = cx - 0.3 + i * 0.15
        mat = ("Cable", "CableRed", "Cable", "CableGreen", "Cable")[i]
        pts = [(x, FRONT + 0.05, 0.35), (x + 0.02, FRONT - 0.08, 0.15), (x - 0.05 + rnd.uniform(-0.1, 0.1), -0.9, 0.012),
               (x - 0.2 + rnd.uniform(-0.2, 0.2), -1.3 - rnd.uniform(0, 0.3), 0.012)]
        parts.append(hg.cable("RS_FloorCable%d" % i, pts, 0.012, mat, coll))
    for i in range(4):
        y = -0.15 - i * 0.08
        mat = ("Cable", "CableRed", "Cable", "CableGreen")[i]
        parts.append(hg.cable("RS_SideCable%d" % i, [(MAIN_X1 + 0.08, y, 1.7 - i * 0.12), (MAIN_X1 + 0.35, y - 0.05, 1.2 - i * 0.1),
                                                    (MAIN_X1 + 0.3, y - 0.1, 0.4), (MAIN_X1 + 0.45 + i * 0.05, y - 0.3, 0.012)], 0.012, mat, coll))

    obj = hg.join(parts, "SM_RadioStation")
    hg.world_uv(obj, skip=SCREENS)
    return obj, sockets


def radio_toggle(name, coll):
    """Big flat lever. Pivot at the hinge; tilt it around X for up/down (±25°)."""
    parts = [hg.cylinder(name + "_Hinge", 0.016, 0.06, (0, 0, 0), "MetalDark", coll, segments=12, rotation=(0, math.radians(90), 0))]
    parts.append(hg.box(name + "_Arm", (0.022, 0.016, 0.08), (0, 0, 0.04), "MetalDark", coll))
    grip = hg.box(name + "_Grip", (0.05, 0.028, 0.11), (0, 0, 0.13), "Bakelite", coll, bevel=0.01)
    for v in grip.data.vertices:
        v.co.x *= 1 + 0.25 * (v.co.z / 0.055)   # paddle widens to the top
    parts.append(grip)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def beacon(name, coll):
    """Red rotating-light beacon: black base, red glass dome inside a wire cage."""
    parts = [hg.cylinder(name + "_Base", 0.06, 0.04, (0, 0, 0.02), "MetalDark", coll, segments=16)]
    parts.append(hg.sphere(name + "_Dome", 0.05, (0, 0, 0.075), "BeaconRed", coll, segments=16, rings=8, scale=(1, 1, 1.25)))
    parts.append(hg.cylinder(name + "_Lens", 0.051, 0.05, (0, 0, 0.065), "BeaconRed", coll, segments=16))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        p = (0.056 * math.cos(a), 0.056 * math.sin(a))
        parts.append(hg.rod("%s_Cage%d" % (name, k), (p[0], p[1], 0.04), (p[0] * 0.3, p[1] * 0.3, 0.14), 0.0025, "MetalDark", coll, segments=4))
    parts.append(hg.torus(name + "_Ring", 0.056, 0.003, (0, 0, 0.09), "MetalDark", coll, segments=16, ring_segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def red_box(name, coll, size=(0.26, 0.14, 0.42)):
    """Red metal box with the door off (door is SM_Radio_RedBoxDoor). Pivot: back, bottom, centre.
    Inside: a terminal block with a pull handle."""
    w, d, h = size
    t = 0.012
    parts = [hg.box(name + "_Back", (w, t, h), (0, -t / 2, h / 2), "PaintRed", coll)]
    for i, (sx, sz, px, pz) in enumerate(((w, t, 0, h - t / 2), (w, t, 0, t / 2), (t, h, -w / 2 + t / 2, h / 2), (t, h, w / 2 - t / 2, h / 2))):
        parts.append(hg.box("%s_Side%d" % (name, i), (sx, d, sz), (px, -d / 2, pz), "PaintRed", coll, bevel=0.003))
    parts.append(hg.box(name + "_Block", (0.14, 0.04, 0.12), (0, -0.03, h * 0.45), "Bakelite", coll, bevel=0.006))
    parts.append(hg.rod(name + "_HandleL", (-0.04, -0.05, h * 0.45 + 0.03), (-0.04, -0.09, h * 0.45 + 0.03), 0.006, "MetalDark", coll))
    parts.append(hg.rod(name + "_HandleR", (0.04, -0.05, h * 0.45 + 0.03), (0.04, -0.09, h * 0.45 + 0.03), 0.006, "MetalDark", coll))
    parts.append(hg.rod(name + "_HandleBar", (-0.045, -0.09, h * 0.45 + 0.03), (0.045, -0.09, h * 0.45 + 0.03), 0.008, "BeaconRed", coll))
    for i in range(2):
        parts.append(hg.cylinder("%s_Gland%d" % (name, i), 0.014, 0.02, (w / 2 + 0.008, -d / 2, h * (0.6 + 0.15 * i)), "MetalDark", coll, segments=10, rotation=(0, math.radians(90), 0)))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def red_box_door(name, coll, size=(0.26, 0.42)):
    """Door of the red box: louvres at the top, latch handle. Hinge at X=0, leaf runs to +X, faces -Y."""
    w, h = size
    parts = [hg.box(name + "_Leaf", (w, 0.015, h), (w / 2, -0.0075, h / 2), "PaintRed", coll, bevel=0.004)]
    for i in range(4):
        louvre = hg.box("%s_Louvre%d" % (name, i), (w * 0.55, 0.012, 0.018), (w / 2, -0.02, h - 0.06 - i * 0.03), "PaintRed", coll)
        louvre.rotation_euler.x = math.radians(-30)
        parts.append(louvre)
    parts.append(hg.box(name + "_LatchPlate", (0.03, 0.008, 0.09), (w - 0.035, -0.019, h * 0.42), "MetalDark", coll, bevel=0.003))
    parts.append(hg.box(name + "_Latch", (0.015, 0.03, 0.06), (w - 0.035, -0.035, h * 0.42), "MetalDark", coll, bevel=0.004))
    for i, z in enumerate((0.06, h - 0.06)):
        parts.append(hg.cylinder("%s_Hinge%d" % (name, i), 0.007, 0.05, (0, -0.012, z), "MetalDark", coll, segments=8))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def grill_door(name, coll, size=(0.68, 1.0)):
    """Chain-link grill in a steel frame in front of the red box. Hinge at X=0, leaf to +X, faces -Y."""
    w, h = size
    parts = []
    for i, (sx, sz, px, pz) in enumerate(((w, 0.03, w / 2, h - 0.015), (w, 0.03, w / 2, 0.015), (0.03, h, 0.015, h / 2), (0.03, h, w - 0.015, h / 2))):
        parts.append(hg.box("%s_Frame%d" % (name, i), (sx, 0.02, sz), (px, -0.01, pz), "MetalDark", coll, bevel=0.004))
    mesh = hg.plane(name + "_Mesh", (w - 0.03, h - 0.03), (w / 2, -0.01, h / 2), "ChainLink", coll)
    parts.append(mesh)
    parts.append(hg.box(name + "_Hasp", (0.03, 0.025, 0.07), (w - 0.02, -0.03, h * 0.5), "MetalDark", coll, bevel=0.004))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


# --- Furniture and the room ------------------------------------------------------------------------

def attic_wardrobe(name, coll, size=(0.62, 1.3, 2.15)):
    """Tall old wardrobe with a scrolled crest, panelled doors and bracket feet. Faces -X like the
    other wardrobes. Board it up with SM_Board_Nailed_* in the level."""
    d, w, h = size
    parts = [hg.box(name + "_Body", (d, w, h - 0.2), (0, 0, 0.12 + (h - 0.2) / 2), "WoodWorn", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Cornice", (d + 0.08, w + 0.08, 0.07), (-0.02, 0, h - 0.045), "WoodWorn", coll, bevel=0.02))
    pts = [(-w / 2 - 0.04, 0.0), (w / 2 + 0.04, 0.0)]
    n = 24
    for i in range(n + 1):
        y = w / 2 + 0.04 - i * (w + 0.08) / n
        s = y / (w / 2 + 0.04)
        z = 0.04 + 0.13 * math.cos(s * math.pi / 2) ** 2 + 0.05 * math.exp(-((abs(s) - 0.8) / 0.09) ** 2)
        pts.append((y, z))
    crest = profile_extrude(name + "_Crest", pts, 0.05, coll, "WoodWorn")
    crest.location = (-d / 2 + 0.02, 0, h - 0.01)
    parts.append(crest)
    parts.append(hg.box(name + "_Plinth", (d + 0.05, w + 0.05, 0.1), (0, 0, 0.15), "WoodWorn", coll, bevel=0.015))
    for i, sgn in enumerate((-1, 1)):
        yc = sgn * w / 4
        parts.append(hg.box("%s_Door%d" % (name, i), (0.025, w / 2 - 0.05, h - 0.42), (-d / 2 - 0.01, yc, h / 2 + 0.02), "WoodWorn", coll, bevel=0.006))
        for k, (z0, z1) in enumerate(((0.32, 0.95), (1.05, h - 0.3))):
            parts.append(hg.box("%s_Pan%d%d" % (name, i, k), (0.015, w / 2 - 0.2, z1 - z0), (-d / 2 - 0.028, yc, (z0 + z1) / 2), "WoodDark", coll, bevel=0.008))
        parts.append(hg.sphere("%s_Knob%d" % (name, i), 0.024, (-d / 2 - 0.05, sgn * 0.06, h * 0.5), "WoodDark", coll, segments=10, rings=5))
    for i, (x, y) in enumerate(((-d / 2 + 0.05, -w / 2 + 0.06), (-d / 2 + 0.05, w / 2 - 0.06), (d / 2 - 0.05, -w / 2 + 0.06), (d / 2 - 0.05, w / 2 - 0.06))):
        parts.append(hg.box("%s_Foot%d" % (name, i), (0.09, 0.09, 0.1), (x, y, 0.05), "WoodWorn", coll, bevel=0.025))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def nailed_board(name, coll, length, seed):
    """Rough plank for boarding things up: along Y, thickness in X (sits on a -X face), two nails each end."""
    board = hg.box(name + "_Plank", (0.025, length, 0.14), (0, 0, 0), "WoodWeathered", coll, bevel=0.004)
    hg.jitter(board, 0.004, seed=seed)
    parts = [board]
    for i, y in enumerate((-length / 2 + 0.05, length / 2 - 0.05)):
        for k, z in enumerate((-0.035, 0.035)):
            parts.append(hg.cylinder("%s_Nail%d%d" % (name, i, k), 0.008, 0.006, (-0.015, y, z), "MetalDark", coll, segments=8, rotation=(0, math.radians(90), 0)))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def timber(name, coll, size, seed, mat="WoodWorn"):
    """Rough beam, long side along X (rafters, collar beams) or Z (posts)."""
    obj = hg.box(name, size, (0, 0, 0), mat, coll, bevel=0.01)
    hg.jitter(obj, 0.004, seed=seed)
    hg.world_uv(obj)
    return obj


def roof_boards(name, coll, size=(2.0, 2.0), seed=1):
    """Board lining under the roof, lying in XY (tilt it to the roof slope). Boards along X, small gaps."""
    lx, ly = size
    rnd = random.Random(seed)
    parts = []
    width = 0.16
    count = int(ly / width)
    for i in range(count):
        y = -ly / 2 + width / 2 + i * width
        b = hg.box("%s_B%d" % (name, i), (lx, width - 0.012, 0.022), (rnd.uniform(-0.01, 0.01), y, rnd.uniform(-0.004, 0.004)),
                   rnd.choice(("WoodWorn", "WoodWeathered", "WoodWorn")), coll, bevel=0.003)
        parts.append(b)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def skylight(name, coll, broken=False, size=(0.6, 0.75)):
    """Roof window lying in XY (tilt with the roof): deep wooden frame and glass; the broken one has a
    jagged hole in the glass."""
    w, l = size
    parts = []
    for i, (sx, sy, px, py) in enumerate(((w + 0.14, 0.07, 0, l / 2 + 0.035), (w + 0.14, 0.07, 0, -l / 2 - 0.035), (0.07, l, -w / 2 - 0.035, 0), (0.07, l, w / 2 + 0.035, 0))):
        parts.append(hg.box("%s_Frame%d" % (name, i), (sx, sy, 0.14), (px, py, 0), "WoodWorn", coll, bevel=0.008))
    parts.append(hg.box(name + "_Bar", (0.03, l, 0.04), (0, 0, 0.03), "WoodWorn", coll))
    mesh = bpy.data.meshes.new(name + "_Glass")
    bm = bmesh.new()
    outer = [bm.verts.new(p) for p in ((-w / 2, -l / 2, 0.02), (w / 2, -l / 2, 0.02), (w / 2, l / 2, 0.02), (-w / 2, l / 2, 0.02))]
    edges = [bm.edges.new((outer[i], outer[(i + 1) % 4])) for i in range(4)]
    if broken:
        rnd = random.Random(5)
        hole = []
        for k in range(14):
            a = 2 * math.pi * k / 14
            r = rnd.uniform(0.17, 0.26) if k % 2 else rnd.uniform(0.07, 0.14)
            hole.append(bm.verts.new((w * 0.12 + r * math.cos(a), l * 0.08 + r * 1.2 * math.sin(a), 0.02)))
        edges += [bm.edges.new((hole[i], hole[(i + 1) % len(hole)])) for i in range(len(hole))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    bm.to_mesh(mesh)
    bm.free()
    glass = bpy.data.objects.new(name + "_Glass", mesh)
    glass.data.materials.append(hg.material("Glass"))
    coll.objects.link(glass)
    parts.append(glass)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def broken_tower_wall(name, coll, width=1.3, side=1.7, peak=2.35):
    """Gable plank wall of the little tower with a big ragged hole (sky and roof show through).
    Planks vertical in the XZ plane, faces -Y. Pivot: bottom centre."""
    rnd = random.Random(11)
    parts = []
    pw = 0.13
    count = int(round(width / pw))
    hole_c, hole_r = (0.05, 1.25), 0.45
    for i in range(count):
        x = -width / 2 + pw / 2 + i * pw
        top = side + (peak - side) * (1 - abs(x) / (width / 2))
        dx = abs(x - hole_c[0])
        segs = [(0.0, top)]
        if dx < hole_r:
            half = math.sqrt(hole_r ** 2 - dx ** 2)
            lo = hole_c[1] - half * rnd.uniform(0.45, 1.0)
            hi = hole_c[1] + half * rnd.uniform(0.45, 1.0)
            segs = [(0.0, lo), (hi, top)]
        for k, (z0, z1) in enumerate(segs):
            plank = hg.box("%s_P%d%d" % (name, i, k), (pw - 0.008, 0.025, z1 - z0), (x, 0, (z0 + z1) / 2), rnd.choice(("WoodWorn", "WoodWeathered")), coll, bevel=0.004)
            hg.jitter(plank, 0.004, seed=i * 3 + k)
            parts.append(plank)
            # Splinters at the broken ends.
            if len(segs) == 2:
                zb = z1 if k == 0 else z0
                sgn = 1 if k == 0 else -1
                for s in range(2):
                    sx = x + (s - 0.5) * pw * 0.5
                    parts.append(hg.rod("%s_Spl%d%d%d" % (name, i, k, s), (sx, 0, zb), (sx + rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.01), zb + sgn * rnd.uniform(0.03, 0.08)),
                                        0.008, "WoodWeathered", coll, segments=4))
    # Frame: corner posts, sill and the two roof trims.
    for i, x in enumerate((-width / 2 - 0.05, width / 2 + 0.05)):
        parts.append(hg.box("%s_Post%d" % (name, i), (0.1, 0.1, side), (x, 0.03, side / 2), "WoodDark", coll, bevel=0.01))
    parts.append(hg.box(name + "_Sill", (width + 0.2, 0.12, 0.08), (0, 0.0, 0.04), "WoodDark", coll, bevel=0.01))
    for i, sgn in enumerate((-1, 1)):
        p0 = (sgn * (width / 2 + 0.12), -0.03, side - 0.05)
        p1 = (0, -0.03, peak + 0.06)
        trim = hg.rod("%s_Trim%d" % (name, i), p0, p1, 0.045, "WoodDark", coll, segments=6)
        parts.append(trim)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def plank_table(name, coll):
    """Rough table under the tower window: two-plank top, legs, cross brace, a loose board on it."""
    parts = []
    for i, y in enumerate((-0.13, 0.13)):
        parts.append(hg.box("%s_Top%d" % (name, i), (1.3, 0.25, 0.04), (0, y, 0.82), "WoodWorn", coll, bevel=0.005))
    for i, (x, y) in enumerate(((-0.58, -0.2), (-0.58, 0.2), (0.58, -0.2), (0.58, 0.2))):
        parts.append(hg.box("%s_Leg%d" % (name, i), (0.07, 0.07, 0.8), (x, y, 0.4), "WoodWorn", coll, bevel=0.006))
    brace = hg.box(name + "_Brace", (1.3, 0.05, 0.05), (0, 0.2, 0.35), "WoodWorn", coll)
    brace.rotation_euler.y = math.radians(18)
    parts.append(brace)
    loose = hg.box(name + "_Loose", (0.7, 0.18, 0.025), (0.05, -0.02, 0.855), "WoodWeathered", coll, bevel=0.004)
    loose.rotation_euler.z = math.radians(-8)
    parts.append(loose)
    for k in range(3):
        parts.append(hg.box("%s_Paper%d" % (name, k), (0.21, 0.29, 0.002), (-0.35 + k * 0.05, 0.05 - k * 0.02, 0.842 + k * 0.002), "Paper", coll, rotation=(0, 0, math.radians(10 * k - 5))))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def dresser(name, coll):
    """Small dark-red chest of three drawers, the top one pulled out. Faces -X."""
    d, w, h = 0.45, 0.7, 0.85
    parts = [hg.box(name + "_Top", (d + 0.03, w + 0.04, 0.035), (0, 0, h), "WoodPaintedRedDark", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Body", (d, w, h - 0.12), (0, 0, 0.1 + (h - 0.12) / 2), "WoodPaintedRedDark", coll, bevel=0.008))
    for i in range(3):
        z = 0.24 + i * 0.22
        out = 0.14 if i == 2 else 0.0
        if out:
            parts.append(hg.box("%s_DrawerBox%d" % (name, i), (out + 0.02, w - 0.08, 0.17), (-d / 2 - out / 2 + 0.01, 0, z), "WoodWorn", coll))
        parts.append(hg.box("%s_Drawer%d" % (name, i), (0.02, w - 0.06, 0.19), (-d / 2 - 0.01 - out, 0, z), "WoodPaintedRed", coll, bevel=0.005))
        for k, y in enumerate((-0.15, 0.15)):
            parts.append(hg.sphere("%s_Knob%d%d" % (name, i, k), 0.016, (-d / 2 - 0.03 - out, y, z), "Brass", coll, segments=8, rings=4))
    for i, (x, y) in enumerate(((-d / 2 + 0.04, -w / 2 + 0.04), (-d / 2 + 0.04, w / 2 - 0.04), (d / 2 - 0.04, -w / 2 + 0.04), (d / 2 - 0.04, w / 2 - 0.04))):
        parts.append(hg.cylinder("%s_Foot%d" % (name, i), 0.03, 0.1, (x, y, 0.05), "WoodPaintedRedDark", coll, segments=8, radius_top=0.022))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def floor_cables(name, coll, seed=2):
    """Four cables snaking over the floor (about 2.5 m along +X), one ends in a plug."""
    rnd = random.Random(seed)
    parts = []
    for i in range(4):
        y0 = (i - 1.5) * 0.06
        pts = [(0.0, y0, 0.012)]
        for k in range(1, 6):
            pts.append((k * 0.5, y0 + rnd.uniform(-0.25, 0.25), 0.012))
        parts.append(hg.cable("%s_C%d" % (name, i), pts, 0.011, ("Cable", "CableRed", "Cable", "CableGreen")[i], coll))
    end = pts[-1]
    parts.append(hg.box(name + "_Plug", (0.06, 0.035, 0.025), (end[0] + 0.03, end[1], 0.014), "Bakelite", coll, bevel=0.006))
    for k, dy in enumerate((-0.008, 0.008)):
        parts.append(hg.rod("%s_Prong%d" % (name, k), (end[0] + 0.06, end[1] + dy, 0.014), (end[0] + 0.085, end[1] + dy, 0.014), 0.002, "Brass", coll, segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def hanging_cables(name, coll, span=2.5, sag=0.45, seed=4):
    """Three cables drooping between two points span apart along X at Z=0 (hang them from rafters)."""
    rnd = random.Random(seed)
    parts = []
    for i in range(3):
        s = sag * rnd.uniform(0.7, 1.2)
        pts = [(span * t, (i - 1) * 0.04, -s * 4 * t * (1 - t)) for t in (0, 0.2, 0.4, 0.6, 0.8, 1.0)]
        parts.append(hg.cable("%s_C%d" % (name, i), pts, 0.01, ("Cable", "CableRed", "CableGreen")[i], coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def floor_papers(name, coll, seed=6):
    """A few loose sheets on the floor, slightly bent."""
    rnd = random.Random(seed)
    parts = []
    for k in range(5):
        p = hg.box("%s_S%d" % (name, k), (0.21, 0.29, 0.002), (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.4, 0.4), 0.002 + k * 0.001), "Paper", coll,
                   rotation=(rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), rnd.uniform(0, math.pi)))
        parts.append(p)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def transformer(name, coll):
    """Old cylindrical transformer standing on the floor with a cable (Attic_Radio, middle)."""
    parts = [hg.cylinder(name + "_Base", 0.13, 0.08, (0, 0, 0.04), "MetalPainted", coll, segments=18)]
    parts.append(hg.cylinder(name + "_Body", 0.09, 0.22, (0, 0, 0.19), "MetalPainted", coll, segments=18))
    parts.append(hg.cylinder(name + "_Cap", 0.1, 0.03, (0, 0, 0.315), "MetalDark", coll, segments=18))
    for k in range(2):
        parts.append(hg.cylinder("%s_Term%d" % (name, k), 0.012, 0.04, ((k - 0.5) * 0.08, 0, 0.35), "Brass", coll, segments=8))
    parts.append(hg.cable(name + "_Cable", [(0.04, 0, 0.36), (0.1, -0.05, 0.42), (0.25, -0.1, 0.2), (0.4, -0.2, 0.012), (0.9, -0.3, 0.012)], 0.01, "Cable", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Attic")
    station, sockets = radio_station(coll)
    assets = [
        station,
        radio_toggle("SM_Radio_Toggle", coll),
        beacon("SM_Radio_Beacon", coll),
        red_box("SM_Radio_RedBox", coll),
        red_box_door("SM_Radio_RedBoxDoor", coll),
        grill_door("SM_Radio_GrillDoor", coll),
        attic_wardrobe("SM_Wardrobe_Attic", coll),
        nailed_board("SM_Board_Nailed_150", coll, 1.5, seed=1),
        nailed_board("SM_Board_Nailed_100", coll, 1.0, seed=2),
        timber("SM_Attic_Beam_400", coll, (4.0, 0.15, 0.2), seed=1),
        timber("SM_Attic_Rafter_300", coll, (3.0, 0.1, 0.18), seed=2),
        timber("SM_Attic_Post_240", coll, (0.15, 0.15, 2.4), seed=3, mat="WoodDark"),
        roof_boards("SM_Attic_RoofBoards_200", coll),
        skylight("SM_Attic_Skylight", coll),
        skylight("SM_Attic_Skylight_Broken", coll, broken=True),
        broken_tower_wall("SM_Attic_TowerWall_Broken", coll),
        plank_table("SM_Attic_PlankTable", coll),
        dresser("SM_Dresser_Attic", coll),
        floor_cables("SM_Cables_Floor", coll),
        hanging_cables("SM_Cables_Hanging", coll),
        floor_papers("SM_Papers_Floor", coll),
        transformer("SM_Transformer_Old", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    with open(os.path.join(OUT, "RadioStation_sockets.json"), "w", encoding="utf-8") as f:
        json.dump(dict(note="Blender metres/degrees relative to SM_RadioStation's pivot; Unreal: x*100, -y*100, z*100",
                       sockets=sockets), f, indent=2)
    # Lay the kit out in a row for review; the station keeps its puzzle parts in their sockets.
    x = 3.0
    for obj in assets[6:]:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.5) + 0.6
    by_mesh = {o.name: o for o in assets}
    for s in sockets:
        src = by_mesh[s["mesh"]]
        inst = src.copy()
        coll.objects.link(inst)
        inst.name = "Preview_" + s["name"]
        inst.location = s["location"]
        inst.rotation_euler = [math.radians(a) for a in s["rotation"]]
    for name in ("SM_Radio_Toggle", "SM_Radio_Beacon", "SM_Radio_RedBox", "SM_Radio_RedBoxDoor", "SM_Radio_GrillDoor"):
        by_mesh[name].location = (-2.5, -1.5 - 0.5 * list(by_mesh).index(name), 0)
    hg.save_blend(os.path.join(OUT, "Attic_Kit.blend"))
    print("exported %d attic assets to %s" % (len(assets), OUT))


build()
