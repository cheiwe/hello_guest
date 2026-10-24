"""
Player's room (Player_Room concept): bed with ball posts and coloured pillows, desk with a drawer
pedestal, tube chair, small bookcase with books and toys, big sash window with a curtain rod,
posters cut out of the concept, cork board with notes, boombox, tube radio, toys, books, comics,
mug, waste bin, a pile of clothes (cloth simulation) and the striped rug.

Furniture faces -X, wall things (posters, board, window) have their back at Y=0 and face -Y.
"""

import importlib
import math
import os
import random
import sys

import bpy

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "PlayerRoom")
RX = (math.radians(90), 0, 0)
RY = (0, math.radians(90), 0)
POSTERS = {"Beats": (0.42, 0.6), "AstroBoy": (0.38, 0.6), "Robot": (0.42, 0.66), "Attack": (0.45, 0.66),
           "DarkWoods": (0.42, 0.62), "Aircraft": (0.36, 0.52), "Cat": (0.34, 0.5), "Fighters": (0.45, 0.58)}
BOOKS = ("BookRed", "BookGreen", "BookBlue", "BookBrown", "BookOchre")


def player_bed(name, coll, size=(2.0, 0.95)):
    """Wooden bed with turned posts and ball finials, rumpled grey blanket, a white and two coloured
    pillows, a striped throw over the footboard. Head at +X."""
    l, w = size
    rnd = random.Random(3)
    parts = []
    for end, (x, ph) in enumerate(((l / 2, 1.0), (-l / 2, 0.8))):
        parts.append(hg.box("%s_Board%d" % (name, end), (0.05, w, ph - 0.3), (x, 0, 0.3 + (ph - 0.3) / 2), "WoodPanel", coll, bevel=0.012))
        for k, y in enumerate((-w / 2, w / 2)):
            parts.append(hg.cylinder("%s_Post%d%d" % (name, end, k), 0.045, ph, (x, y, ph / 2), "WoodPanel", coll, segments=12))
            parts.append(hg.torus("%s_Ring%d%d" % (name, end, k), 0.047, 0.012, (x, y, ph - 0.12), "WoodPanel", coll, segments=12, ring_segments=6))
            parts.append(hg.sphere("%s_Ball%d%d" % (name, end, k), 0.075, (x, y, ph + 0.065), "WoodPanel", coll, segments=14, rings=7))
    for k, y in enumerate((-w / 2, w / 2)):
        parts.append(hg.box("%s_Rail%d" % (name, k), (l, 0.045, 0.2), (0, y, 0.32), "WoodPanel", coll, bevel=0.01))
    parts.append(hg.box(name + "_Mattress", (l - 0.08, w - 0.06, 0.2), (0, 0, 0.47), "Fabric_Light", coll, bevel=0.05))
    blanket = hg.box(name + "_Blanket", (l * 0.62, w + 0.06, 0.07), (-l * 0.1, 0, 0.6), "Blanket_Grey", coll, bevel=0.03)
    for v in blanket.data.vertices:
        v.co.z += 0.03 * math.sin(v.co.x * 9 + 1) * math.cos(v.co.y * 7)
    hg.jitter(blanket, 0.02, seed=7)
    parts.append(blanket)
    for i, (x, y, mat) in enumerate(((l / 2 - 0.3, -0.18, "Fabric_Light"), (l / 2 - 0.42, 0.2, "PillowRed"), (0.0, 0.18, "PillowYellow"))):
        pillow = hg.box("%s_Pillow%d" % (name, i), (0.38, 0.5 if i == 0 else 0.4, 0.13), (x, y, 0.64 + 0.02 * i), mat, coll, bevel=0.06)
        pillow.rotation_euler.z = math.radians(rnd.uniform(-20, 20))
        hg.jitter(pillow, 0.012, seed=8 + i)
        parts.append(pillow)
    throw = hg.box(name + "_Throw", (0.06, w * 0.5, 0.5), (-l / 2 - 0.04, -0.1, 0.55), "Throw", coll, bevel=0.02)
    hg.jitter(throw, 0.015, seed=11)
    parts.append(throw)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def player_desk(name, coll):
    """Pine desk with a three-drawer pedestal on the right and a thin drawer on the left. Faces -X."""
    d, w, h = 0.65, 1.3, 0.76
    parts = [hg.box(name + "_Top", (d, w, 0.035), (0, 0, h - 0.0175), "WoodPanel", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Ped", (d - 0.04, 0.42, h - 0.1), (0.01, w / 2 - 0.23, (h - 0.1) / 2 + 0.06), "WoodPanel", coll, bevel=0.008))
    for k, (z, hh) in enumerate(((h - 0.12, 0.13), (0.42, 0.2), (0.17, 0.2))):
        parts.append(hg.box("%s_Dr%d" % (name, k), (0.02, 0.38, hh), (-d / 2 + 0.005, w / 2 - 0.23, z), "WoodPanel", coll, bevel=0.006))
        parts.append(hg.sphere("%s_Knob%d" % (name, k), 0.018, (-d / 2 - 0.015, w / 2 - 0.23, z), "WoodDark", coll, segments=8, rings=4))
    parts.append(hg.box(name + "_DrL", (0.02, 0.5, 0.09), (-d / 2 + 0.03, -0.15, h - 0.08), "WoodPanel", coll, bevel=0.005))
    parts.append(hg.sphere(name + "_KnobL", 0.016, (-d / 2 + 0.01, -0.15, h - 0.08), "WoodDark", coll, segments=8, rings=4))
    for i, (x, y) in enumerate(((-d / 2 + 0.04, -w / 2 + 0.04), (d / 2 - 0.04, -w / 2 + 0.04))):
        parts.append(hg.box("%s_Leg%d" % (name, i), (0.05, 0.05, h - 0.03), (x, y, (h - 0.03) / 2), "WoodPanel", coll, bevel=0.006))
    for i, (x, y) in enumerate(((-d / 2 + 0.05, w / 2 - 0.05), (d / 2 - 0.05, w / 2 - 0.05), (-d / 2 + 0.05, w / 2 - 0.41), (d / 2 - 0.05, w / 2 - 0.41))):
        parts.append(hg.cylinder("%s_Foot%d" % (name, i), 0.03, 0.06, (x, y, 0.03), "WoodPanel", coll, segments=8, radius_top=0.024))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def tube_chair(name, coll):
    """50s school chair: bent chrome tube frame, padded grey seat and backrest. Faces -X."""
    parts = []
    for k, y in enumerate((-0.2, 0.2)):
        pts = [(-0.22, y, 0.0), (-0.2, y, 0.44), (0.18, y, 0.44), (0.2, y, 0.0)]
        parts.append(hg.cable("%s_FrameLow%d" % (name, k), pts, 0.011, "Chrome", coll, segments=8))
        parts.append(hg.rod("%s_BackPost%d" % (name, k), (0.18, y, 0.44), (0.24, y, 0.88), 0.011, "Chrome", coll))
        parts.append(hg.sphere("%s_Cap%d" % (name, k), 0.013, (-0.22, y, 0.0), "Rubber", coll, segments=8, rings=4))
        parts.append(hg.sphere("%s_CapB%d" % (name, k), 0.013, (0.2, y, 0.0), "Rubber", coll, segments=8, rings=4))
    parts.append(hg.rod(name + "_Cross", (-0.2, -0.2, 0.42), (-0.2, 0.2, 0.42), 0.009, "Chrome", coll))
    parts.append(hg.box(name + "_Seat", (0.44, 0.44, 0.06), (0, 0, 0.48), "Vinyl", coll, bevel=0.025))
    back = hg.box(name + "_Back", (0.04, 0.42, 0.26), (0.235, 0, 0.78), "Vinyl", coll, bevel=0.015)
    back.rotation_euler.y = math.radians(-8)
    parts.append(back)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def book_row(name, coll, y0, y1, z, depth=0.22, seed=0, lean_last=True):
    """Books standing on a shelf between y0 and y1 at height z (spines to -X)."""
    rnd = random.Random(seed)
    parts = []
    y = y0
    i = 0
    while y < y1 - 0.03:
        t = rnd.uniform(0.025, 0.045)
        hgt = rnd.uniform(0.18, 0.28)
        b = hg.box("%s_B%d" % (name, i), (depth * rnd.uniform(0.75, 1.0), t, hgt), (0, y + t / 2, z + hgt / 2), rnd.choice(BOOKS), coll, bevel=0.003)
        parts.append(b)
        y += t + 0.002
        i += 1
    if lean_last and parts:
        parts[-1].rotation_euler.x = math.radians(-14)
    return parts


def bookcase(name, coll):
    """Small open bookcase (1.25 m) with books, a couple of toys and a lying stack. Faces -X."""
    d, w, h = 0.3, 0.75, 1.25
    parts = []
    for k, y in enumerate((-w / 2 + 0.01, w / 2 - 0.01)):
        parts.append(hg.box("%s_Side%d" % (name, k), (d, 0.02, h), (0, y, h / 2), "WoodPanel", coll, bevel=0.005))
    parts.append(hg.box(name + "_Back", (0.01, w, h), (d / 2 - 0.005, 0, h / 2), "WoodPanel", coll))
    shelves = (0.05, 0.36, 0.66, 0.95, h - 0.01)
    for k, z in enumerate(shelves):
        parts.append(hg.box("%s_Shelf%d" % (name, k), (d, w - 0.02, 0.02), (0, 0, z), "WoodPanel", coll, bevel=0.003))
    parts.append(hg.box(name + "_Kick", (0.02, w - 0.02, 0.06), (-d / 2 + 0.01, 0, 0.03), "WoodPanel", coll))
    for k, z in enumerate(shelves[:3]):
        books = book_row("%s_Row%d" % (name, k), coll, -w / 2 + 0.03, w / 2 - (0.25 if k == 1 else 0.03), z + 0.01, seed=k + 1)
        for b in books:
            b.location.x += 0.02
        parts += books
    for k in range(4):
        parts.append(hg.box("%s_Lying%d" % (name, k), (0.2, 0.28, 0.03), (0.0, 0.0, shelves[3] + 0.025 + k * 0.032), BOOKS[k], coll, bevel=0.003,
                            rotation=(0, 0, math.radians(8 * k - 10))))
    parts += robot_parts(name + "_Robot", coll, (-0.02, 0.24, shelves[1] + 0.01), 0.6)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def sash_window(name, coll, w=1.5, h=1.55):
    """Big double-hung window: casing, two sashes with a meeting rail, sill, curtain rod with ball
    ends above. Sits in a wall opening of w x h; bottom of the opening at Z=0, wall face at Y=0."""
    parts = []
    t = 0.09
    for i, (sx, sz, px, pz) in enumerate(((w + 2 * t, t, 0, h + t / 2), (t, h, -w / 2 - t / 2, h / 2), (t, h, w / 2 + t / 2, h / 2))):
        parts.append(hg.box("%s_Casing%d" % (name, i), (sx, 0.03, sz), (px, -0.015, pz), "Trim", coll, bevel=0.008))
    parts.append(hg.box(name + "_Sill", (w + 0.3, 0.14, 0.04), (0, -0.04, -0.02), "Trim", coll, bevel=0.01))
    for k, (z0, z1, y) in enumerate(((0.0, h / 2 + 0.02, 0.05), (h / 2 - 0.02, h, 0.1))):
        st = 0.05
        for i, (sx, sz, px, pz) in enumerate(((w, st, 0, z0 + st / 2), (w, st, 0, z1 - st / 2), (st, z1 - z0, -w / 2 + st / 2, (z0 + z1) / 2), (st, z1 - z0, w / 2 - st / 2, (z0 + z1) / 2))):
            parts.append(hg.box("%s_Sash%d%d" % (name, k, i), (sx, 0.04, sz), (px, y, pz), "Trim", coll, bevel=0.005))
        parts.append(hg.plane("%s_Glass%d" % (name, k), (w - 2 * st, z1 - z0 - 2 * st), (0, y, (z0 + z1) / 2), "Glass", coll))
    for k, x in enumerate((-0.35, 0.35)):
        parts.append(hg.box("%s_Lock%d" % (name, k), (0.05, 0.02, 0.015), (x, 0.02, h / 2 + 0.03), "Brass", coll, bevel=0.003))
    rod_z = h + 0.22
    parts.append(hg.rod(name + "_Rod", (-w / 2 - 0.35, -0.1, rod_z), (w / 2 + 0.35, -0.1, rod_z), 0.014, "WoodDark", coll))
    for k, x in enumerate((-w / 2 - 0.37, w / 2 + 0.37)):
        parts.append(hg.sphere("%s_Finial%d" % (name, k), 0.035, (x, -0.1, rod_z), "WoodDark", coll, segments=12, rings=6))
        parts.append(hg.rod("%s_Bracket%d" % (name, k), (x * 0.95, 0, rod_z), (x * 0.95, -0.1, rod_z), 0.01, "Brass", coll, segments=6))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def poster_mesh(name, coll, size, mat):
    """Paper poster slightly curling at the corners, back at Y=0, picture to -Y."""
    w, h = size
    p = hg.plane(name, (w, h), (0, -0.003, 0), mat, coll)
    mod = p.modifiers.new("Sub", "SUBSURF")
    mod.subdivision_type = "SIMPLE"
    mod.levels = 3
    bpy.ops.object.select_all(action="DESELECT")
    p.select_set(True)
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.modifier_apply(modifier="Sub")
    for v in p.data.vertices:
        cx, cz = abs(v.co.x) / (w / 2), abs(v.co.z) / (h / 2)
        v.co.y -= 0.012 * (max(cx, cz) ** 6)
    hg.apply_transforms(p)
    return p


def cork_board(name, coll):
    """Cork board in a wooden frame with pinned notes and drawings (above the desk)."""
    rnd = random.Random(9)
    w, h = 0.6, 0.48
    parts = [hg.box(name + "_Cork", (w, 0.015, h), (0, -0.0075, 0), "Cork", coll)]
    for i, (sx, sz, px, pz) in enumerate(((w + 0.04, 0.02, 0, h / 2 + 0.01), (w + 0.04, 0.02, 0, -h / 2 - 0.01), (0.02, h, -w / 2 - 0.01, 0), (0.02, h, w / 2 + 0.01, 0))):
        parts.append(hg.box("%s_Frame%d" % (name, i), (sx, 0.025, sz), (px, -0.0125, pz), "WoodPanel", coll, bevel=0.004))
    for k in range(7):
        nw, nh = rnd.uniform(0.08, 0.15), rnd.uniform(0.08, 0.13)
        x, z = rnd.uniform(-w / 2 + 0.08, w / 2 - 0.08), rnd.uniform(-h / 2 + 0.07, h / 2 - 0.07)
        note = hg.plane("%s_Note%d" % (name, k), (nw, nh), (x, -0.017 - k * 0.0006, z), "Paper", coll, rotation=(0, math.radians(rnd.uniform(-8, 8)), 0))
        parts.append(note)
        parts.append(hg.sphere("%s_Pin%d" % (name, k), 0.006, (x, -0.022 - k * 0.0006, z + nh / 2 - 0.012), rnd.choice(("PaintRed", "PaintBlue", "PaintYellow")), coll, segments=8, rings=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def boombox(name, coll):
    """Grey radio-cassette: two speaker grilles, cassette deck, tuner strip, handle. Front faces -X."""
    parts = [hg.box(name + "_Body", (0.12, 0.42, 0.22), (0, 0, 0.11), "MetalPainted", coll, bevel=0.015)]
    for k, y in enumerate((-0.13, 0.13)):
        parts.append(hg.cylinder("%s_Spk%d" % (name, k), 0.065, 0.02, (-0.06, y, 0.1), "Bakelite", coll, segments=20, rotation=RY))
        parts.append(hg.torus("%s_SpkRim%d" % (name, k), 0.066, 0.006, (-0.07, y, 0.1), "Chrome", coll, rotation=RY, segments=20, ring_segments=4))
    parts.append(hg.box(name + "_Deck", (0.01, 0.11, 0.07), (-0.062, 0, 0.09), "Bakelite", coll, bevel=0.004))
    parts.append(hg.box(name + "_Tuner", (0.01, 0.36, 0.03), (-0.062, 0, 0.19), "Gauge", coll))
    for k in range(5):
        parts.append(hg.box("%s_Key%d" % (name, k), (0.03, 0.016, 0.012), (0.0, -0.04 + k * 0.02, 0.225), "Chrome", coll, bevel=0.002))
    for k, y in enumerate((-0.17, 0.17)):
        parts.append(hg.rod("%s_HandlePost%d" % (name, k), (0, y, 0.22), (0, y, 0.27), 0.008, "Chrome", coll, segments=6))
    parts.append(hg.rod(name + "_Handle", (0, -0.17, 0.27), (0, 0.17, 0.27), 0.01, "Chrome", coll))
    parts.append(hg.rod(name + "_Antenna", (0.04, 0.18, 0.22), (0.07, 0.25, 0.5), 0.003, "Chrome", coll, segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def tube_radio(name, coll):
    """Wooden tabletop tube radio on the floor by the bed: rounded case, cloth grille, dial, knobs."""
    parts = [hg.box(name + "_Case", (0.2, 0.42, 0.26), (0, 0, 0.13), "WoodPanel", coll, bevel=0.035)]
    parts.append(hg.box(name + "_Grille", (0.01, 0.3, 0.12), (-0.1, 0, 0.16), "Fabric", coll, bevel=0.01))
    for k in range(5):
        parts.append(hg.box("%s_Slat%d" % (name, k), (0.008, 0.3, 0.008), (-0.106, 0, 0.11 + k * 0.025), "WoodDark", coll))
    parts.append(hg.box(name + "_Dial", (0.008, 0.26, 0.035), (-0.1, 0, 0.06), "Gauge", coll, bevel=0.004))
    for k, y in enumerate((-0.17, 0.17)):
        parts.append(hg.cylinder("%s_Knob%d" % (name, k), 0.02, 0.02, (-0.11, y, 0.06), "Bakelite", coll, segments=12, rotation=RY))
    parts.append(hg.rod(name + "_Antenna", (0.05, 0.15, 0.26), (0.0, 0.3, 0.55), 0.003, "Chrome", coll, segments=4))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def robot_parts(name, coll, base, scale=1.0):
    """Tin toy robot (bookshelf, ATTACK poster style): box body, head with antenna, arms, feet."""
    bx, by, bz = base
    s = scale

    def p(x, y, z):
        return (bx + x * s, by + y * s, bz + z * s)

    parts = [hg.box(name + "_Body", (0.06 * s, 0.1 * s, 0.11 * s), p(0, 0, 0.12), "TinBlue", coll, bevel=0.008 * s)]
    parts.append(hg.box(name + "_Head", (0.06 * s, 0.07 * s, 0.06 * s), p(0, 0, 0.21), "TinBlue", coll, bevel=0.008 * s))
    for k, y in enumerate((-0.017, 0.017)):
        parts.append(hg.sphere("%s_Eye%d" % (name, k), 0.009 * s, p(-0.031, y, 0.215), "PaintYellow", coll, segments=8, rings=4))
    parts.append(hg.box(name + "_Panel", (0.005, 0.06 * s, 0.05 * s), p(-0.031, 0, 0.12), "PaintRed", coll))
    parts.append(hg.rod(name + "_Ant", p(0, 0, 0.24), p(0, 0, 0.28), 0.002 * s, "Chrome", coll, segments=4))
    parts.append(hg.sphere(name + "_AntBall", 0.007 * s, p(0, 0, 0.283), "PaintRed", coll, segments=8, rings=4))
    for k, y in enumerate((-0.063, 0.063)):
        parts.append(hg.box("%s_Arm%d" % (name, k), (0.025 * s, 0.022 * s, 0.09 * s), p(0, y, 0.12), "Chrome", coll, bevel=0.004 * s))
        parts.append(hg.box("%s_Leg%d" % (name, k), (0.03 * s, 0.035 * s, 0.06 * s), p(0, y * 0.45, 0.035), "Chrome", coll, bevel=0.004 * s))
        parts.append(hg.box("%s_Foot%d" % (name, k), (0.05 * s, 0.04 * s, 0.015 * s), p(-0.008, y * 0.45, 0.0075), "TinBlue", coll, bevel=0.003 * s))
    return parts


def toy_robot(name, coll):
    obj = hg.join(robot_parts(name, coll, (0, 0, 0)), name)
    hg.world_uv(obj, scale=4.0)
    return obj


def toy_car(name, coll, body="PaintRed"):
    """Tin toy car: rounded body, cabin with windows, four wheels. Nose to -X."""
    parts = [hg.box(name + "_Body", (0.16, 0.06, 0.03), (0, 0, 0.025), body, coll, bevel=0.012)]
    parts.append(hg.box(name + "_Cabin", (0.07, 0.05, 0.03), (0.01, 0, 0.05), body, coll, bevel=0.01))
    parts.append(hg.box(name + "_Window", (0.072, 0.052, 0.015), (0.01, 0, 0.055), "Glass", coll, bevel=0.005))
    for k, (x, y) in enumerate(((-0.05, -0.03), (-0.05, 0.03), (0.05, -0.03), (0.05, 0.03))):
        parts.append(hg.cylinder("%s_Wheel%d" % (name, k), 0.014, 0.012, (x, y, 0.014), "Rubber", coll, segments=12, rotation=RX))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def toy_figure(name, coll):
    """Little action figure (on the bookcase and the shelf): legs, torso, arms, head, red cape."""
    parts = []
    for k, y in enumerate((-0.012, 0.012)):
        parts.append(hg.cylinder("%s_Leg%d" % (name, k), 0.009, 0.06, (0, y, 0.03), "PaintBlue", coll, segments=8))
        parts.append(hg.cylinder("%s_Arm%d" % (name, k), 0.007, 0.05, (0, y * 2.6, 0.085), "Skin", coll, segments=8))
    parts.append(hg.box(name + "_Torso", (0.025, 0.045, 0.05), (0, 0, 0.085), "PaintRed", coll, bevel=0.006))
    parts.append(hg.sphere(name + "_Head", 0.016, (0, 0, 0.128), "Skin", coll, segments=10, rings=6))
    parts.append(hg.box(name + "_Cape", (0.006, 0.05, 0.07), (0.016, 0, 0.075), "PillowRed", coll, bevel=0.002))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def book_stack(name, coll, count=6, seed=2):
    rnd = random.Random(seed)
    parts = []
    z = 0.0
    for k in range(count):
        t = rnd.uniform(0.025, 0.05)
        parts.append(hg.box("%s_B%d" % (name, k), (rnd.uniform(0.17, 0.24), rnd.uniform(0.24, 0.3), t), (rnd.uniform(-0.01, 0.01), 0, z + t / 2), rnd.choice(BOOKS), coll,
                            bevel=0.003, rotation=(0, 0, math.radians(rnd.uniform(-10, 10)))))
        z += t
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def comics(name, coll, count=5, seed=3):
    """A few comic books, the top one with a cover picture, fanned out on the floor."""
    rnd = random.Random(seed)
    parts = []
    for k in range(count):
        c = hg.box("%s_C%d" % (name, k), (0.17, 0.26, 0.004), (rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), 0.002 + k * 0.0042),
                   "Paper" if k < count - 1 else "Comic", coll, rotation=(0, 0, math.radians(rnd.uniform(-25, 25))))
        if k == count - 1:
            hg.face_uv(c, "xy")
        parts.append(c)
    obj = hg.join(parts, name)
    hg.world_uv(obj, skip=("Comic",))
    return obj


def mug(name, coll):
    parts = [hg.cylinder(name + "_Body", 0.04, 0.095, (0, 0, 0.0475), "Porcelain", coll, segments=16)]
    parts.append(hg.cylinder(name + "_Coffee", 0.036, 0.004, (0, 0, 0.085), "WoodDark", coll, segments=16))
    parts.append(hg.torus(name + "_Handle", 0.025, 0.007, (0.045, 0, 0.05), "Porcelain", coll, rotation=RX, segments=12, ring_segments=6, scale=(0.8, 1, 1.1)))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def waste_bin(name, coll):
    """Green tin waste-paper bin, slightly tapered, with a rolled rim and a crumpled paper inside."""
    parts = [hg.cylinder(name + "_Body", 0.15, 0.36, (0, 0, 0.18), "TinGreen", coll, segments=20, radius_top=0.17)]
    parts.append(hg.torus(name + "_Rim", 0.17, 0.008, (0, 0, 0.36), "TinGreen", coll, segments=20, ring_segments=6))
    ball = hg.sphere(name + "_Paper", 0.05, (0.02, 0.03, 0.3), "Paper", coll, segments=8, rings=5)
    hg.jitter(ball, 0.012, seed=4)
    parts.append(ball)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def soft_lump(name, coll, size, loc, mat, seed, rot=0.0):
    """Soft heap of fabric: a rounded box, subdivided and pushed about by noise, folds pressed in."""
    obj = hg.box(name, size, loc, mat, coll, bevel=min(size) * 0.45, rotation=(0, 0, rot))
    sub = obj.modifiers.new("Sub", "SUBSURF")
    sub.levels = 2
    tex = bpy.data.textures.new(name + "_Noise", "CLOUDS")
    tex.noise_scale = 0.12
    disp = obj.modifiers.new("Disp", "DISPLACE")
    disp.texture = tex
    disp.strength = min(size) * 0.5
    disp.mid_level = 0.5
    disp.texture_coords = "GLOBAL"
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for m in ("Sub", "Disp"):
        bpy.ops.object.modifier_apply(modifier=m)
    rnd = random.Random(seed)
    # Folds: a few creases pressed into the top.
    for _ in range(3):
        a = rnd.uniform(0, math.pi)
        off = rnd.uniform(-0.1, 0.1)
        for v in obj.data.vertices:
            d = (v.co.x - loc[0]) * math.sin(a) - (v.co.y - loc[1]) * math.cos(a) - off
            if v.co.z > loc[2]:
                v.co.z -= 0.025 * math.exp(-(d / 0.03) ** 2)
    bpy.data.textures.remove(tex)
    return obj


def clothes_pile(name, coll):
    """Heap of clothes on the floor (Player_Room, by the bookcase): soft lumps of a green, a blue and a
    white garment, a folded shirt on top, a sleeve hanging down to the floor, two socks."""
    parts = [soft_lump(name + "_Green", coll, (0.75, 0.6, 0.26), (0, 0, 0.13), "ClothGreen", 1, rot=0.3),
             soft_lump(name + "_Blue", coll, (0.5, 0.42, 0.2), (0.08, 0.05, 0.3), "ClothBlue", 2, rot=-0.4),
             soft_lump(name + "_White", coll, (0.36, 0.3, 0.14), (-0.06, -0.06, 0.42), "Fabric_Light", 3, rot=0.9)]
    shirt = hg.box(name + "_Shirt", (0.34, 0.28, 0.045), (0.05, 0.03, 0.5), "PillowRed", coll, bevel=0.02, rotation=(0.1, -0.06, 0.5))
    hg.jitter(shirt, 0.008, seed=12)
    parts.append(shirt)
    parts.append(hg.cable(name + "_Sleeve", [(0.15, 0.12, 0.48), (0.28, 0.2, 0.42), (0.38, 0.26, 0.25), (0.42, 0.3, 0.04), (0.55, 0.36, 0.025)], 0.035, "PillowRed", coll, segments=8))
    for k, (p0, p1) in enumerate((((-0.55, 0.3, 0.025), (-0.36, 0.42, 0.025)), ((0.48, -0.42, 0.025), (0.62, -0.28, 0.03)))):
        parts.append(hg.cable("%s_Sock%d" % (name, k), [p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 0.03, 0.035), p1], 0.025, "Fabric_Light", coll, segments=8))
    obj = hg.join(parts, name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    hg.world_uv(obj)
    return obj


def player_rug(name, coll, size=(2.2, 1.4)):
    obj = hg.box(name, (size[0], size[1], 0.012), (0, 0, 0.006), "Rug_Player", coll)
    hg.planar_uv(obj)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_PlayerRoom")
    assets = [
        player_bed("SM_Bed_Player", coll),
        player_desk("SM_Desk_Player", coll),
        tube_chair("SM_Chair_Tube", coll),
        bookcase("SM_Bookcase_Player", coll),
        sash_window("SM_Window_Sash_150", coll),
        cork_board("SM_CorkBoard", coll),
        boombox("SM_Boombox", coll),
        tube_radio("SM_Radio_Tube", coll),
        toy_robot("SM_Toy_Robot", coll),
        toy_car("SM_Toy_Car_Red", coll),
        toy_car("SM_Toy_Car_Green", coll, body="TinGreen"),
        toy_figure("SM_Toy_Figure", coll),
        book_stack("SM_Books_Stack", coll),
        comics("SM_Comics_Floor", coll),
        mug("SM_Mug", coll),
        waste_bin("SM_WasteBin", coll),
        clothes_pile("SM_Clothes_Pile", coll),
        player_rug("SM_Rug_Player", coll),
    ]
    for key, size in POSTERS.items():
        p = poster_mesh("SM_Poster_" + key, coll, size, "Poster_" + key)
        assets.append(p)
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.4) + 0.5
    hg.save_blend(os.path.join(OUT, "PlayerRoom_Kit.blend"))
    print("exported %d player room assets to %s" % (len(assets), OUT))


build()
