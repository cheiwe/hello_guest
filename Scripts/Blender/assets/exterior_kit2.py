"""
Exterior kit, part 2 (Street_Example, Yard_01-03, Outhouse, Ufo_above_the_roof): attic tower with a
pyramid roof and a metal spire, porch, brick chimney, fences (plank, picket, chain-link), the outhouse and
the satellite dish.
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


def boards_wall(prefix, x0, x1, z0, z1, y, coll, parts, seed=0, mat="WoodWeathered", vertical=True, gap=0.008):
    """Row of rough vertical boards with uneven tops (outhouse, plank fence)."""
    rnd = random.Random(seed)
    x = x0
    i = 0
    while x < x1 - 0.02:
        bw = min(rnd.uniform(0.1, 0.16), x1 - x)
        top = z1 + rnd.uniform(-0.04, 0.04)
        b = hg.box("%s_B%d" % (prefix, i), (bw - gap, 0.025, top - z0), (x + bw / 2, y, (z0 + top) / 2), mat, coll, bevel=0.004)
        b.rotation_euler.y = math.radians(rnd.uniform(-1.2, 1.2))
        hg.jitter(b, 0.004, seed=seed * 31 + i)
        parts.append(b)
        x += bw
        i += 1


def tower(name, coll, size=2.6, wall_h=2.8, roof_h=3.2, spire_h=1.6):
    """Attic tower: clapboard box with a small arched window on each side, steep pyramid roof, metal spire."""
    s = size / 2
    parts = [hg.box(name + "_Core", (size - 0.06, size - 0.06, wall_h), (0, 0, wall_h / 2), "Plaster", coll)]
    rnd = random.Random(3)
    for side in range(4):
        a = side * math.pi / 2
        z = 0.0
        i = 0
        while z < wall_h - 0.01:
            h = min(0.16, wall_h - z)
            b = hg.box("%s_C%d_%d" % (name, side, i), (size, 0.022, h + 0.02), (0, -s, z + h / 2), "Siding", coll, bevel=0.004)
            b.rotation_euler.x = math.radians(-3)
            b.location.z += rnd.uniform(-0.004, 0.004)
            hg.rotate_about_z(b, a)
            parts.append(b)
            z += h
            i += 1
        # Narrow window with a pointed head (the gothic one on the concept).
        for nm, size_, loc in (("Glass", (0.45, 0.02, 0.85), (0, -s - 0.02, 1.35)),
                               ("CasL", (0.07, 0.04, 1.0), (-0.26, -s - 0.03, 1.4)),
                               ("CasR", (0.07, 0.04, 1.0), (0.26, -s - 0.03, 1.4)),
                               ("Sill", (0.62, 0.1, 0.05), (0, -s - 0.05, 0.9))):
            p = hg.box("%s_%s%d" % (name, nm, side), size_, loc, "Glass" if nm == "Glass" else "Trim", coll, bevel=0.006)
            hg.rotate_about_z(p, a)
            parts.append(p)
        for k, sgn in enumerate((-1, 1)):
            p = hg.box("%s_Arch%d_%d" % (name, side, k), (0.36, 0.05, 0.07), (sgn * 0.13, -s - 0.03, 1.98), "Trim", coll, bevel=0.006)
            p.rotation_euler.y = math.radians(sgn * 35)
            hg.rotate_about_z(p, a)
            parts.append(p)
        # Corner boards.
        cb = hg.box("%s_Corner%d" % (name, side), (0.1, 0.1, wall_h), (-s, -s, wall_h / 2), "Trim", coll, bevel=0.006)
        hg.rotate_about_z(cb, a)
        parts.append(cb)
    # Eave band and the pyramid roof with a metal spire and a ball.
    parts.append(hg.box(name + "_Eave", (size + 0.3, size + 0.3, 0.14), (0, 0, wall_h + 0.07), "Trim", coll, bevel=0.02))
    roof = hg.cylinder(name + "_Roof", (size + 0.35) / math.sqrt(2), roof_h, (0, 0, wall_h + 0.14 + roof_h / 2), "Shingle", coll, segments=4, radius_top=0.08)
    roof.rotation_euler.z = math.radians(45)
    parts.append(roof)
    top = wall_h + 0.14 + roof_h
    parts.append(hg.cylinder(name + "_SpireBase", 0.12, 0.25, (0, 0, top + 0.05), "MetalDark", coll, segments=8))
    parts.append(hg.cylinder(name + "_Spire", 0.07, spire_h, (0, 0, top + 0.18 + spire_h / 2), "MetalDark", coll, segments=8, radius_top=0.004))
    parts.append(hg.sphere(name + "_Ball", 0.09, (0, 0, top + 0.45), "MetalDark", coll, segments=12, rings=6))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def porch(name, coll, width=2.6, depth=1.6, floor_h=0.4, post_h=2.5):
    """Front porch: deck on the house side (+Y in Blender is the house), three steps, two posts, a small roof."""
    parts = [hg.box(name + "_Deck", (width, depth, 0.08), (0, -depth / 2, floor_h - 0.04), "WoodWeathered", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Skirt", (width - 0.05, depth - 0.05, floor_h - 0.08), (0, -depth / 2, (floor_h - 0.08) / 2), "WoodDark", coll))
    for i in range(3):
        z = floor_h * (2 - i) / 3
        parts.append(hg.box("%s_Step%d" % (name, i), (1.3, 0.3, 0.05), (0, -depth - 0.15 - i * 0.28, z - 0.025), "WoodWeathered", coll, bevel=0.008))
        parts.append(hg.box("%s_Riser%d" % (name, i), (1.3, 0.04, z), (0, -depth - 0.02 - i * 0.28, z / 2), "WoodDark", coll))
    for i, x in enumerate((-width / 2 + 0.12, width / 2 - 0.12)):
        parts.append(hg.box("%s_Post%d" % (name, i), (0.12, 0.12, post_h), (x, -depth + 0.12, floor_h + post_h / 2), "Trim", coll, bevel=0.01))
        for k in range(5):
            parts.append(hg.box("%s_Bal%d_%d" % (name, i, k), (0.04, 0.04, 0.75), (x * (1 - 0.13 * (k + 1)), -depth + 0.12, floor_h + 0.4), "Trim", coll))
        parts.append(hg.box("%s_Rail%d" % (name, i), (width / 2 - 0.75, 0.07, 0.06), (x * 0.62, -depth + 0.12, floor_h + 0.8), "Trim", coll, bevel=0.01))
    roof = hg.box(name + "_Roof", (width + 0.4, depth + 0.5, 0.08), (0, -depth / 2 - 0.15, floor_h + post_h + 0.2), "Shingle", coll, bevel=0.01)
    # Slopes down towards the street (-Y).
    roof.rotation_euler.x = math.radians(18)
    parts.append(roof)
    parts.append(hg.box(name + "_Beam", (width, 0.14, 0.18), (0, -depth + 0.12, floor_h + post_h), "Trim", coll, bevel=0.01))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def chimney(name, coll, height=2.4):
    parts = [hg.box(name + "_Stack", (0.7, 0.55, height), (0, 0, height / 2), "Brick", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Cap", (0.85, 0.7, 0.12), (0, 0, height + 0.06), "Concrete", coll, bevel=0.015))
    for i, x in enumerate((-0.14, 0.14)):
        parts.append(hg.cylinder("%s_Pot%d" % (name, i), 0.09, 0.3, (x, 0, height + 0.27), "Brick", coll, segments=10))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def plank_fence(name, coll, length=2.0, height=2.3, seed=5):
    """Tall weathered plank fence, uneven pointed tops (Yard_01-03). Runs along +X, boards face -Y."""
    parts = []
    boards_wall(name, 0, length, 0, height, 0, coll, parts, seed=seed)
    for i, z in enumerate((0.35, height - 0.4)):
        parts.append(hg.box("%s_Rail%d" % (name, i), (length, 0.05, 0.1), (length / 2, 0.04, z), "WoodWeathered", coll, bevel=0.008))
    for i, x in enumerate((0.05, length - 0.05)):
        parts.append(hg.box("%s_Post%d" % (name, i), (0.1, 0.1, height - 0.1), (x, 0.08, (height - 0.1) / 2), "WoodDark", coll, bevel=0.01))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def picket_fence(name, coll, length=2.0, height=1.0, seed=6):
    """White picket fence of the player's house (Street_Example)."""
    rnd = random.Random(seed)
    parts = []
    n = int(length / 0.14)
    for i in range(n):
        x = 0.07 + i * length / n
        h = height + rnd.uniform(-0.02, 0.02)
        parts.append(hg.box("%s_P%d" % (name, i), (0.08, 0.022, h - 0.08), (x, 0, (h - 0.08) / 2), "Trim", coll, bevel=0.004))
        tip = hg.cylinder("%s_T%d" % (name, i), 0.055, 0.1, (x, 0, h - 0.03), "Trim", coll, segments=4, radius_top=0.002)
        tip.scale = (1, 0.25, 1)
        tip.rotation_euler.z = math.radians(45)
        parts.append(tip)
    for i, z in enumerate((0.25, height - 0.25)):
        parts.append(hg.box("%s_Rail%d" % (name, i), (length, 0.04, 0.07), (length / 2, 0.03, z), "Trim", coll, bevel=0.006))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def chainlink_fence(name, coll, length=2.0, height=2.0):
    """Chain-link panel: metal posts and rails, the mesh is one plane with a masked diamond texture."""
    parts = []
    for i, x in enumerate((0.0, length)):
        parts.append(hg.cylinder("%s_Post%d" % (name, i), 0.03, height + 0.05, (x, 0, (height + 0.05) / 2), "MetalRust", coll, segments=10))
    parts.append(hg.rod(name + "_Top", (0, 0, height), (length, 0, height), 0.02, "MetalRust", coll))
    mesh = hg.plane(name + "_Mesh", (length, height - 0.05), (length / 2, 0, (height - 0.05) / 2 + 0.03), "ChainLink", coll)
    # Tile the diamond texture: one tile = 0.5 m.
    for loop in mesh.data.uv_layers[0].data:
        loop.uv = (loop.uv[0] * length * 2, loop.uv[1] * (height - 0.05) * 2)
    parts.append(mesh)
    obj = hg.join(parts, name)
    return obj


def outhouse(name, coll, seed=9):
    """Outhouse from the Outhouse concept: crooked board walls, moss on the gable roof, crescent moon in the
    door, planks nailed across. Door faces -X."""
    rnd = random.Random(seed)
    w, d, h = 1.05, 1.15, 2.1
    parts = [hg.box(name + "_Floor", (w + 0.1, d + 0.1, 0.1), (0, 0, 0.05), "WoodWeathered", coll)]
    for side, (rot, off) in enumerate(((0, -d / 2), (math.pi, -d / 2), (math.pi / 2, -w / 2), (-math.pi / 2, -w / 2))):
        sub = []
        span = w if side < 2 else d
        boards_wall("%s_W%d" % (name, side), -span / 2, span / 2, 0.08, h, off, coll, sub, seed=seed + side)
        for b in sub:
            hg.rotate_about_z(b, rot)
        parts += sub
    # Gable fill above the walls (front and back), as stacked short boards.
    for side, x in enumerate((-w / 2, w / 2)):
        for k in range(4):
            z = h + 0.08 * k + 0.04
            half = (d / 2 + 0.05) * (1 - (k + 1) / 5)
            parts.append(hg.box("%s_G%d_%d" % (name, side, k), (0.025, half * 2, 0.08), (x, 0, z), "WoodWeathered", coll))
    # Roof: two slopes with mossy shingles, overhanging.
    for i, sgn in enumerate((-1, 1)):
        slope = hg.box("%s_Roof%d" % (name, i), (w + 0.35, d / 2 + 0.3, 0.05), (0, sgn * (d / 4 + 0.08), h + 0.2), "ShingleMoss", coll, bevel=0.01)
        slope.rotation_euler.x = math.radians(-sgn * 30)
        parts.append(slope)
    # Door on the -X face with a crescent moon and hinges, planks nailed over it.
    door_x = -w / 2 - 0.03
    parts.append(hg.box(name + "_Door", (0.03, 0.72, 1.8), (door_x, 0, 0.98), "WoodWeathered", coll, bevel=0.006))
    # Crescent moon cut-out: a thick dark arc, open towards +Y.
    cy, cz, r = 0.05, 1.55, 0.07
    steps = 9
    for i in range(steps):
        a0 = math.radians(60 + 240 * i / steps)
        a1 = math.radians(60 + 240 * (i + 1) / steps)
        thick = 0.012 + 0.018 * math.sin(math.pi * (i + 0.5) / steps)
        parts.append(hg.rod("%s_Moon%d" % (name, i), (door_x - 0.02, cy + math.cos(a0) * r, cz + math.sin(a0) * r),
                            (door_x - 0.02, cy + math.cos(a1) * r, cz + math.sin(a1) * r), thick, "WoodDark", coll))
    for z in (0.5, 1.5):
        parts.append(hg.box("%s_Hinge%.1f" % (name, z), (0.01, 0.18, 0.04), (door_x - 0.02, -0.28, z), "MetalRust", coll))
    for i, (z, ang) in enumerate(((0.55, 12), (1.05, -8), (1.35, 14))):
        p = hg.box("%s_Plank%d" % (name, i), (0.035, 1.25, 0.15), (door_x - 0.05, 0, z), "WoodWeathered", coll, bevel=0.006)
        p.rotation_euler.x = math.radians(ang)
        hg.jitter(p, 0.006, seed=seed + 40 + i)
        parts.append(p)
    # Grass tufts and moss at the base.
    for i in range(10):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.6, 0.75)
        tuft = hg.cylinder("%s_Grass%d" % (name, i), 0.07, rnd.uniform(0.15, 0.3), (math.cos(a) * r, math.sin(a) * r, 0.1), "Moss", coll, segments=5, radius_top=0.005)
        parts.append(tuft)
    obj = hg.join(parts, name)
    # Lean the whole hut a little, like the drawing.
    for v in obj.data.vertices:
        v.co.y += v.co.z * 0.03
    hg.world_uv(obj)
    return obj


def satellite_dish(name, coll):
    """Small dented rusty dish with a feed arm, clamped to the spire (Ufo_above_the_roof)."""
    parts = []
    dish = hg.sphere(name + "_Dish", 0.35, (0, 0, 0), "MetalRust", coll, segments=20, rings=10, scale=(1, 1, 0.35))
    parts.append(dish)
    parts.append(hg.rod(name + "_Arm", (0, 0, 0.05), (0, 0, 0.42), 0.012, "MetalDark", coll))
    parts.append(hg.sphere(name + "_Feed", 0.035, (0, 0, 0.44), "MetalDark", coll, segments=10, rings=5))
    parts.append(hg.box(name + "_Clamp", (0.08, 0.08, 0.16), (0, 0.0, -0.18), "MetalDark", coll, bevel=0.01))
    obj = hg.join(parts, name)
    # Dish faces up-forward; cut the back half of the sphere away is not needed: it is flattened.
    obj.rotation_euler.y = math.radians(-50)
    hg.apply_transforms(obj)
    hg.world_uv(obj, scale=2.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Exterior2")
    assets = [
        tower("SM_Ext_Tower", coll),
        porch("SM_Ext_Porch", coll),
        chimney("SM_Ext_Chimney", coll),
        plank_fence("SM_Fence_Plank_200", coll),
        picket_fence("SM_Fence_Picket_200", coll),
        chainlink_fence("SM_Fence_ChainLink_200", coll),
        outhouse("SM_Outhouse", coll),
        satellite_dish("SM_SatelliteDish", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.5) + 1.0
    hg.save_blend(os.path.join(OUT, "Exterior_Kit2.blend"))
    print("exported %d exterior assets to %s" % (len(assets), OUT))


build()
