"""
Exterior kit of the neighbour house (Street_Example, Yard_01-03): clapboard walls one storey high,
windows (plain and boarded), the front doorway, a corner board and a shingle roof panel.

Wall modules: pivot bottom-left, run along +X, outside face towards -Y (Blender) = +Y in Unreal,
3.0 m high (floor to the next floor, covering the slab edge). The inside face is dressed like the
interior walls (wainscot + wallpaper) up to the 2.8 m ceiling.
"""

import importlib
import math
import os
import random
import sys

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Exterior")

STOREY = 3.0
WALL_T = 0.22
BOARD = 0.16       # clapboard exposure
WIN_W, WIN_H, SILL = 0.9, 1.45, 0.85
DOOR_W, DOOR_H = 1.2, 2.5


def clapboards(prefix, x0, x1, z0, z1, y, coll, parts, seed=0):
    """Overlapping horizontal boards on the outside face (towards -Y), slightly uneven like the concept."""
    rnd = random.Random(seed)
    z = z0
    i = 0
    while z < z1 - 0.01:
        h = min(BOARD, z1 - z)
        board = hg.box("%s_Cb%d" % (prefix, i), (x1 - x0, 0.022, h + 0.02), ((x0 + x1) / 2, y - 0.011, z + h / 2), "Siding", coll, bevel=0.004)
        # Each board leans out at the bottom (lap siding) and sags a little.
        board.rotation_euler.x = math.radians(-3.0)
        board.location.z += rnd.uniform(-0.004, 0.004)
        parts.append(board)
        z += h
        i += 1


def inside_face(prefix, x0, x1, y, coll, parts, z0=0.0, z1=2.8):
    """Interior dressing: wainscot, chair rail, wallpaper, baseboard (towards +Y)."""
    width = x1 - x0
    cx = (x0 + x1) / 2
    panel = min(0.95, z1)
    if z0 < panel:
        parts.append(hg.box(prefix + "_Pan", (width, 0.02, panel - z0), (cx, y + 0.01, (z0 + panel) / 2), "WoodPanel", coll))
    if z1 > panel:
        bottom = max(panel, z0)
        parts.append(hg.box(prefix + "_Pap", (width, 0.004, z1 - bottom), (cx, y + 0.002, (bottom + z1) / 2), "Wallpaper", coll))
        parts.append(hg.box(prefix + "_Rail", (width, 0.05, 0.05), (cx, y + 0.025, panel), "WoodDark", coll, bevel=0.008))
    if z0 <= 0:
        parts.append(hg.box(prefix + "_Base", (width, 0.03, 0.12), (cx, y + 0.03, 0.06), "WoodDark", coll, bevel=0.006))


def siding_wall(name, width, coll, seed=0):
    parts = [hg.box(name + "_Core", (width, WALL_T - 0.04, STOREY), (width / 2, 0, STOREY / 2), "Plaster", coll)]
    clapboards(name, 0, width, 0, STOREY, -WALL_T / 2 + 0.02, coll, parts, seed)
    inside_face(name + "_In", 0, width, WALL_T / 2 - 0.02, coll, parts)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def window_frame(prefix, x0, x1, z0, z1, coll, parts, boarded=False, seed=0):
    """Double-hung window: outer casing, sill, two sashes with muntins, dirty glass. Boarded: planks nailed over."""
    rnd = random.Random(seed)
    yo = -WALL_T / 2 - 0.01
    t = 0.09
    w = x1 - x0
    cx = (x0 + x1) / 2
    # Casing.
    parts.append(hg.box(prefix + "_CasL", (t, 0.04, z1 - z0 + t), (x0 - t / 2, yo - 0.02, (z0 + z1) / 2 + t / 2), "Trim", coll, bevel=0.008))
    parts.append(hg.box(prefix + "_CasR", (t, 0.04, z1 - z0 + t), (x1 + t / 2, yo - 0.02, (z0 + z1) / 2 + t / 2), "Trim", coll, bevel=0.008))
    head = hg.box(prefix + "_Head", (w + 2 * t + 0.08, 0.06, t + 0.03), (cx, yo - 0.03, z1 + t / 2 + 0.015), "Trim", coll, bevel=0.01)
    parts.append(head)
    parts.append(hg.box(prefix + "_Sill", (w + 2 * t + 0.06, 0.12, 0.05), (cx, yo - 0.05, z0 - 0.02), "Trim", coll, bevel=0.01))
    # Sashes and glass, set back into the opening.
    ys = 0.0
    mid = (z0 + z1) / 2
    for i, (a, b) in enumerate(((z0, mid + 0.02), (mid - 0.02, z1))):
        yy = ys + (-0.02 if i else 0.02)
        for j, (sx, sz, px, pz) in enumerate(((w, 0.05, cx, a + 0.025), (w, 0.05, cx, b - 0.025), (0.05, b - a, x0 + 0.025, (a + b) / 2), (0.05, b - a, x1 - 0.025, (a + b) / 2))):
            parts.append(hg.box("%s_Sash%d_%d" % (prefix, i, j), (sx, 0.04, sz), (px, yy, pz), "Trim", coll))
        parts.append(hg.box("%s_MunV%d" % (prefix, i), (0.025, 0.03, b - a), (cx, yy, (a + b) / 2), "Trim", coll))
        parts.append(hg.box("%s_MunH%d" % (prefix, i), (w, 0.03, 0.025), (cx, yy, (a + b) / 2), "Trim", coll))
        parts.append(hg.box("%s_Glass%d" % (prefix, i), (w - 0.06, 0.008, b - a - 0.06), (cx, yy, (a + b) / 2), "Glass", coll))
    if boarded:
        for i in range(4):
            z = z0 + 0.15 + i * (z1 - z0 - 0.3) / 3
            plank = hg.box("%s_Board%d" % (prefix, i), (w + 0.35, 0.03, 0.17), (cx, yo - 0.07, z), "WoodWeathered", coll, bevel=0.006)
            plank.rotation_euler.y = math.radians(rnd.uniform(-9, 9))
            hg.jitter(plank, 0.006, seed=seed + i)
            parts.append(plank)
            for k, nx in enumerate((x0 - 0.1, x1 + 0.1)):
                parts.append(hg.cylinder("%s_Nail%d_%d" % (prefix, i, k), 0.008, 0.01, (nx, yo - 0.09, z), "MetalDark", coll, segments=6, rotation=(math.radians(90), 0, 0)))


def opening_wall(name, width, coll, x0, x1, z0, z1, seed=0):
    """Siding wall with one rectangular opening; the frame is added by the caller."""
    parts = []
    t = WALL_T - 0.04
    pieces = [(0, x0, 0, STOREY), (x1, width, 0, STOREY), (x0, x1, z1, STOREY)]
    if z0 > 0:
        pieces.append((x0, x1, 0, z0))
    for i, (a, b, c, d) in enumerate(pieces):
        parts.append(hg.box("%s_Core%d" % (name, i), (b - a, t, d - c), ((a + b) / 2, 0, (c + d) / 2), "Plaster", coll))
        clapboards("%s_P%d" % (name, i), a, b, c, d, -WALL_T / 2 + 0.02, coll, parts, seed + i)
        inside_face("%s_In%d" % (name, i), a, b, WALL_T / 2 - 0.02, coll, parts, z0=c, z1=min(d, 2.8))
    # Reveal (the inside of the opening).
    for i, (sx, sz, px, pz) in enumerate(((0.03, z1 - z0, x0 + 0.015, (z0 + z1) / 2), (0.03, z1 - z0, x1 - 0.015, (z0 + z1) / 2), (x1 - x0, 0.03, (x0 + x1) / 2, z1 - 0.015))):
        parts.append(hg.box("%s_Rev%d" % (name, i), (sx, WALL_T, sz), (px, 0, pz), "Trim", coll))
    return parts


def window_wall(name, width, coll, boarded=False, seed=0):
    x0 = (width - WIN_W) / 2
    parts = opening_wall(name, width, coll, x0, x0 + WIN_W, SILL, SILL + WIN_H, seed)
    window_frame(name + "_W", x0, x0 + WIN_W, SILL, SILL + WIN_H, coll, parts, boarded, seed)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def door_wall(name, width, coll, seed=0):
    x0 = (width - DOOR_W) / 2
    x1 = x0 + DOOR_W
    parts = opening_wall(name, width, coll, x0, x1, 0, DOOR_H, seed)
    t = 0.1
    yo = -WALL_T / 2 - 0.03
    parts.append(hg.box(name + "_CasL", (t, 0.05, DOOR_H + t), (x0 - t / 2, yo, (DOOR_H + t) / 2), "Trim", coll, bevel=0.008))
    parts.append(hg.box(name + "_CasR", (t, 0.05, DOOR_H + t), (x1 + t / 2, yo, (DOOR_H + t) / 2), "Trim", coll, bevel=0.008))
    parts.append(hg.box(name + "_Head", (DOOR_W + 2 * t + 0.1, 0.08, t + 0.05), ((x0 + x1) / 2, yo - 0.01, DOOR_H + t / 2 + 0.03), "Trim", coll, bevel=0.012))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def corner_board(name, coll, height=STOREY):
    """Vertical corner trim covering the clapboard ends where two walls meet."""
    parts = [hg.box(name + "_A", (0.12, 0.03, height), (0.06 - 0.015, -0.015, height / 2), "Trim", coll, bevel=0.006),
             hg.box(name + "_B", (0.03, 0.12, height), (-0.015, 0.06 - 0.015, height / 2), "Trim", coll, bevel=0.006)]
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def shingle_panel(name, coll, size=(1.0, 1.0), seed=8):
    """1 x 1 m roof panel of chunky, uneven shingles in rows (Street_Example, Yard_03). Lies flat:
    rows run along X, the slope goes up along +Y; rotate it onto the roof."""
    rnd = random.Random(seed)
    w, d = size
    parts = [hg.box(name + "_Deck", (w, d, 0.02), (0, 0, -0.01), "WoodDark", coll)]
    row = 0.2
    rows = int(d / row)
    for r in range(rows):
        y = -d / 2 + r * row + row / 2
        x = -w / 2 + (0.0 if r % 2 == 0 else -0.12)
        while x < w / 2:
            sw = rnd.uniform(0.18, 0.3)
            a, b = max(x, -w / 2), min(x + sw - 0.012, w / 2)
            if b - a > 0.04:
                sh = hg.box("%s_S%d_%.2f" % (name, r, x), (b - a, row + 0.07, 0.025), ((a + b) / 2, y + 0.02, 0.015 + rnd.uniform(0, 0.006)), "Shingle", coll, bevel=0.005)
                sh.rotation_euler.x = math.radians(-4)
                sh.rotation_euler.z = math.radians(rnd.uniform(-1.5, 1.5))
                parts.append(sh)
            x += sw
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=1.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Exterior")
    assets = [
        siding_wall("SM_Ext_Wall_100", 1.0, coll, seed=1),
        siding_wall("SM_Ext_Wall_200", 2.0, coll, seed=2),
        siding_wall("SM_Ext_Wall_50", 0.5, coll, seed=3),
        window_wall("SM_Ext_Window_160", 1.6, coll, seed=4),
        window_wall("SM_Ext_WindowBoarded_160", 1.6, coll, boarded=True, seed=5),
        door_wall("SM_Ext_Door_200", 2.0, coll, seed=6),
        corner_board("SM_Ext_CornerBoard", coll),
        shingle_panel("SM_Roof_Shingles_100", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.5) + 0.6
    hg.save_blend(os.path.join(OUT, "Exterior_Kit.blend"))
    print("exported %d exterior assets to %s" % (len(assets), OUT))


build()
