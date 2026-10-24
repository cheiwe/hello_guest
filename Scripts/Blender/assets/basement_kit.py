"""
Basements: the fuse basement (Basement_Fusebox concept) and the secret basement where Vitec streams
(Secret_Basement concept).

Fuse basement: rusty fuse box (doors and the fuse are separate: the fuse is a puzzle item), knife
switch with a separate lever, pipes with hangers, water heater, furniture under sheets (Blender cloth
simulation), wooden chairs, puddles, brick and concrete wall panels.
Secret basement: CRT monitors, VCRs, VHS tapes, the old desk with mixers, keyboard and mouse, red desk
lamp, office chair, PC tower, concrete stairs, junction box with cables.

Wall-mounted things: back at Y=0, front to -Y. Furniture faces -X like the other kits.
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

OUT = os.path.join(hg.MODELS_DIR, "Basement")
RX = (math.radians(90), 0, 0)   # cylinder axis along Y (faces -Y)
RY = (0, math.radians(90), 0)   # cylinder axis along X


def blob(name, coll, radius, seed, mat, z=0.0, thickness=0.004, points=18):
    """Flat irregular blob lying on the floor (puddles)."""
    rnd = random.Random(seed)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    radii = [radius * rnd.uniform(0.6, 1.1) for _ in range(points)]
    radii = [(radii[i - 1] + 2 * radii[i] + radii[(i + 1) % points]) / 4 for i in range(points)]
    verts = [bm.verts.new((r * math.cos(2 * math.pi * i / points) * 1.3, r * math.sin(2 * math.pi * i / points), z + thickness)) for i, r in enumerate(radii)]
    face = bm.faces.new(verts)
    bmesh.ops.triangulate(bm, faces=[face])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material(mat))
    coll.objects.link(obj)
    return obj


# --- Fuse basement ---------------------------------------------------------------------------------

def fuse_box(name, coll, size=(0.62, 0.2, 0.7)):
    """Rusty wall cabinet, doors off (SM_FuseBox_Door, hinges at the outer edges). Inside: a tangle
    of old wires around a porcelain fuse block with two cartridge slots, one of them empty (the
    puzzle: the player brings SM_Fuse). Cable glands on the right side with cables going down."""
    w, d, h = size
    t = 0.015
    rnd = random.Random(21)
    parts = [hg.box(name + "_Back", (w, t, h), (0, -t / 2, h / 2), "MetalRust", coll)]
    for i, (sx, sz, px, pz) in enumerate(((w, t, 0, h - t / 2), (w, t, 0, t / 2), (t, h, -w / 2 + t / 2, h / 2), (t, h, w / 2 - t / 2, h / 2))):
        parts.append(hg.box("%s_Side%d" % (name, i), (sx, d, sz), (px, -d / 2, pz), "MetalRust", coll, bevel=0.004))
    parts.append(hg.box(name + "_Divider", (0.012, d * 0.9, h - 0.03), (0, -d * 0.45, h / 2), "MetalRust", coll))
    # Fuse block on the right half: porcelain base, brass clips, one fuse in place.
    bx, bz = w / 4, h * 0.48
    parts.append(hg.box(name + "_Block", (0.16, 0.05, 0.26), (bx, -0.04, bz), "Porcelain", coll, bevel=0.01))
    for k, zz in enumerate((bz + 0.06, bz - 0.06)):
        for c, dx in enumerate((-0.04, 0.04)):
            parts.append(hg.box("%s_Clip%d%d" % (name, k, c), (0.02, 0.03, 0.03), (bx + dx, -0.075, zz), "Brass", coll, bevel=0.004))
    parts += fuse_parts(name + "_Fuse", coll, (bx, -0.08, bz + 0.06))
    # Wires: loops from the top and the bottom into the block.
    for i in range(9):
        x0 = -w / 2 + 0.06 + i * (w - 0.12) / 8
        side = 1 if i % 2 else -1
        pts = [(x0, -0.03, h - 0.02), (x0 + rnd.uniform(-0.05, 0.05), -0.1, h * 0.8), (bx + side * 0.09 + rnd.uniform(-0.03, 0.03), -0.12, bz + 0.12 * side),
               (bx + rnd.uniform(-0.06, 0.06), -0.07, bz + side * 0.02)]
        if x0 < 0:
            pts = [(x0, -0.03, h - 0.02), (x0 + rnd.uniform(-0.04, 0.04), -0.12, h * rnd.uniform(0.3, 0.7)), (x0 + 0.05, -0.1, 0.06), (x0 + 0.1, -0.03, 0.03)]
        parts.append(hg.cable("%s_Wire%d" % (name, i), pts, 0.006, rnd.choice(("Cable", "CableRed", "Cable", "Brass")), coll))
    # Cable glands on the right side and the thick cables going down the wall.
    for i, z in enumerate((h * 0.42, h * 0.3)):
        parts.append(hg.cylinder("%s_Gland%d" % (name, i), 0.03, 0.04, (w / 2 + 0.02, -d / 2, z), "Brass", coll, segments=12, rotation=RY))
        parts.append(hg.torus("%s_GlandRing%d" % (name, i), 0.03, 0.008, (w / 2 + 0.04, -d / 2, z), "MetalRust", coll, rotation=RY, segments=12, ring_segments=6))
        parts.append(hg.cable("%s_Out%d" % (name, i), [(w / 2 + 0.03, -d / 2, z), (w / 2 + 0.15, -d / 2 + 0.02, z - 0.05), (w / 2 + 0.22, -0.05, z - 0.3), (w / 2 + 0.25, -0.04, -0.9)],
                              0.018, "Cable", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def fuse_box_door(name, coll, size=(0.31, 0.7)):
    """One leaf of the fuse box: rusty sheet with a pressed border. Hinge at X=0, leaf to +X, faces -Y."""
    w, h = size
    parts = [hg.box(name + "_Leaf", (w, 0.012, h), (w / 2, -0.006, h / 2), "MetalRust", coll, bevel=0.003)]
    for i, (sx, sz, px, pz) in enumerate(((w - 0.04, 0.012, w / 2, h - 0.03), (w - 0.04, 0.012, w / 2, 0.03), (0.012, h - 0.06, 0.03, h / 2), (0.012, h - 0.06, w - 0.03, h / 2))):
        parts.append(hg.box("%s_Rib%d" % (name, i), (sx, 0.008, sz), (px, -0.015, pz), "MetalRust", coll))
    parts.append(hg.box(name + "_Latch", (0.02, 0.02, 0.06), (w - 0.03, -0.022, h / 2), "MetalDark", coll, bevel=0.004))
    for i, z in enumerate((0.08, h - 0.08)):
        parts.append(hg.cylinder("%s_Hinge%d" % (name, i), 0.008, 0.06, (0, -0.012, z), "MetalDark", coll, segments=8))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def fuse_parts(name, coll, centre):
    """Cartridge fuse along X: porcelain body, brass end caps."""
    x, y, z = centre
    parts = [hg.cylinder(name + "_Body", 0.013, 0.07, (x, y, z), "Porcelain", coll, segments=12, rotation=RY)]
    for k, dx in enumerate((-0.042, 0.042)):
        parts.append(hg.cylinder("%s_Cap%d" % (name, k), 0.015, 0.016, (x + dx, y, z), "Brass", coll, segments=12, rotation=RY))
    return parts


def fuse(name, coll):
    obj = hg.join(fuse_parts(name, coll, (0, 0, 0.015)), name)
    hg.world_uv(obj, scale=4.0)
    return obj


def knife_switch(name, coll):
    """Big wall knife switch: iron box with a slotted front and a terminal cover, cables up from the top.
    The lever is SM_KnifeSwitch_Lever (pivot on the hinge axle, see the socket in the docstring of
    knife_switch_lever)."""
    parts = [hg.box(name + "_Back", (0.34, 0.03, 0.5), (0, -0.015, 0), "MetalDark", coll, bevel=0.008)]
    parts.append(hg.box(name + "_Box", (0.26, 0.14, 0.3), (0, -0.09, 0.06), "MetalPainted", coll, bevel=0.025))
    parts.append(hg.box(name + "_Slot", (0.05, 0.02, 0.22), (0, -0.16, 0.04), "MetalDark", coll, bevel=0.005))
    for k, z in enumerate((0.21, -0.21)):
        for c, x in enumerate((-0.14, 0.14)):
            parts.append(hg.cylinder("%s_Bolt%d%d" % (name, k, c), 0.014, 0.02, (x, -0.035, z), "MetalDark", coll, segments=6, rotation=RX))
    parts.append(hg.box(name + "_Terminal", (0.2, 0.1, 0.1), (0, -0.07, -0.17), "MetalPainted", coll, bevel=0.015))
    for i, x in enumerate((-0.05, 0.05)):
        parts.append(hg.cable("%s_Cable%d" % (name, i), [(x, -0.07, 0.2), (x * 1.5, -0.08, 0.45), (x * 2.2 - 0.05, -0.06, 0.9), (x * 2.2 - 0.1, -0.05, 1.4)], 0.022, "Cable", coll))
        parts.append(hg.cable("%s_Low%d" % (name, i), [(x, -0.07, -0.21), (x + 0.05, -0.12, -0.35), (x + 0.12, -0.1, -0.55), (x + 0.3, -0.06, -0.7)], 0.016, "Cable", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def knife_switch_lever(name, coll):
    """Lever of the knife switch. Pivot on the hinge axle; rotate around X: 0° = up (on), 160° = down.
    Socket on SM_KnifeSwitch: (0, -0.17, 0.04)."""
    parts = [hg.cylinder(name + "_Axle", 0.02, 0.12, (0, 0, 0), "MetalDark", coll, segments=12, rotation=RY)]
    for k, x in enumerate((-0.035, 0.035)):
        parts.append(hg.box("%s_Arm%d" % (name, k), (0.015, 0.03, 0.28), (x, -0.01, 0.14), "MetalPainted", coll, bevel=0.005))
    grip = hg.box(name + "_Grip", (0.11, 0.05, 0.11), (0, -0.02, 0.32), "Bakelite", coll, bevel=0.02)
    parts.append(grip)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def pipe(name, coll, length=2.0, radius=0.045, mat="MetalRust"):
    """Straight pipe along X with a coupling at each end."""
    parts = [hg.cylinder(name + "_Tube", radius, length, (length / 2, 0, 0), mat, coll, segments=14, rotation=RY)]
    for k, x in enumerate((0.03, length - 0.03)):
        parts.append(hg.cylinder("%s_Coupling%d" % (name, k), radius * 1.3, 0.06, (x, 0, 0), mat, coll, segments=14, rotation=RY))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def pipe_elbow(name, coll, radius=0.045, bend=0.15, mat="MetalRust"):
    """90° elbow from +X to +Z: in along X at the origin, out up along Z."""
    pts = [(0, 0, 0)]
    for k in range(1, 7):
        a = k / 6 * math.pi / 2
        pts.append((bend * math.sin(a), 0, bend * (1 - math.cos(a))))
    pts.append((bend, 0, bend + 0.05))
    parts = [hg.cable(name + "_Bend", pts, radius, mat, coll, segments=14)]
    parts.append(hg.cylinder(name + "_C0", radius * 1.3, 0.06, (0.0, 0, 0), mat, coll, segments=14, rotation=RY))
    parts.append(hg.cylinder(name + "_C1", radius * 1.3, 0.06, (bend, 0, bend + 0.04), mat, coll, segments=14))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def ceiling_pipes(name, coll, length=4.0, seed=31):
    """Bundle of pipes under the ceiling along X (pivot at the ceiling, Z=0, pipes hang below),
    hangers every metre, cobwebby sag on a cable run alongside."""
    rnd = random.Random(seed)
    parts = []
    runs = [(-0.25, -0.12, 0.05), (-0.05, -0.15, 0.035), (0.12, -0.11, 0.06), (0.3, -0.2, 0.03)]
    for i, (y, z, r) in enumerate(runs):
        parts.append(hg.cylinder("%s_P%d" % (name, i), r, length, (length / 2, y, z), "MetalRust" if i != 1 else "MetalPainted", coll, segments=14, rotation=RY))
        for k in range(int(length) + 1):
            x = min(max(k * 1.0, 0.05), length - 0.05)
            parts.append(hg.cylinder("%s_J%d%d" % (name, i, k), r * 1.25, 0.05, (x + rnd.uniform(-0.1, 0.1), y, z), "MetalRust", coll, segments=14, rotation=RY))
    for k in range(int(length)):
        x = 0.5 + k
        parts.append(hg.box("%s_Hanger%d" % (name, k), (0.03, 0.7, 0.012), (x, 0.02, -0.03), "MetalDark", coll))
        for i, (y, z, r) in enumerate(runs):
            parts.append(hg.rod("%s_Strap%d%d" % (name, k, i), (x, y, -0.03), (x, y, z - r), 0.006, "MetalDark", coll, segments=4))
    pts = [(length * t, 0.4, -0.05 - 0.12 * math.sin(math.pi * t * 4) ** 2) for t in (0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0)]
    parts.append(hg.cable(name + "_Cable", pts, 0.012, "Cable", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def water_heater(name, coll):
    """Rusty tank water heater on short legs: dome top, flue pipe up, cold/hot pipes with valves,
    drain valve and a burner hatch at the bottom, label plate."""
    r, h = 0.27, 1.35
    parts = [hg.cylinder(name + "_Tank", r, h, (0, 0, 0.12 + h / 2), "MetalRust", coll, segments=28)]
    parts.append(hg.sphere(name + "_Dome", r, (0, 0, 0.12 + h), "MetalRust", coll, segments=28, rings=10, scale=(1, 1, 0.28)))
    parts.append(hg.cylinder(name + "_Base", r * 1.02, 0.12, (0, 0, 0.17), "MetalDark", coll, segments=28))
    for k in range(3):
        a = k * 2 * math.pi / 3
        parts.append(hg.cylinder("%s_Leg%d" % (name, k), 0.025, 0.12, (0.85 * r * math.cos(a), 0.85 * r * math.sin(a), 0.06), "MetalDark", coll, segments=8))
    for k, z in enumerate((0.45, 1.1)):
        parts.append(hg.torus("%s_Band%d" % (name, k), r + 0.004, 0.008, (0, 0, z), "MetalDark", coll, segments=28, ring_segments=4))
    parts.append(hg.cylinder(name + "_Flue", 0.06, 0.9, (0, 0, 0.12 + h + 0.5), "MetalPainted", coll, segments=14))
    for i, y in enumerate((-0.12, 0.12)):
        top = (0.0, y, 0.12 + h + 0.03)
        parts.append(hg.rod("%s_Riser%d" % (name, i), top, (0.0, y, 2.3), 0.025, "MetalRust", coll, segments=10))
        parts.append(hg.cylinder("%s_Valve%d" % (name, i), 0.035, 0.07, (0.0, y, 1.75), "Brass", coll, segments=10))
        parts.append(hg.torus("%s_Wheel%d" % (name, i), 0.045, 0.007, (-0.06, y, 1.75), "PaintRed", coll, rotation=RY, segments=14, ring_segments=4))
        parts.append(hg.rod("%s_Stem%d" % (name, i), (0.0, y, 1.75), (-0.06, y, 1.75), 0.006, "MetalDark", coll, segments=4))
    # Side pipe with a valve, running from low on the tank to the wall behind.
    parts.append(hg.rod(name + "_SideOut", (-r + 0.02, 0, 0.6), (-r - 0.12, 0, 0.6), 0.02, "MetalRust", coll, segments=10))
    parts.append(hg.cylinder(name + "_SideValve", 0.03, 0.06, (-r - 0.14, 0, 0.6), "Brass", coll, segments=10, rotation=RY))
    parts.append(hg.rod(name + "_SideUp", (-r - 0.14, 0, 0.6), (-r - 0.14, 0, 1.25), 0.02, "MetalRust", coll, segments=10))
    parts.append(hg.box(name + "_Hatch", (0.03, 0.18, 0.12), (-r + 0.005, 0, 0.3), "MetalDark", coll, bevel=0.01))
    parts.append(hg.box(name + "_Label", (0.01, 0.16, 0.06), (-r + 0.005, 0, 1.25), "Label", coll))
    parts.append(hg.cylinder(name + "_Drain", 0.015, 0.06, (-r - 0.02, 0.0, 0.22), "Brass", coll, segments=8, rotation=RY))
    for o in parts:
        if o.name.endswith(("_Hatch", "_Label")):
            hg.rotate_about_z(o, math.radians(-30))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def armchair_proxy(name, coll):
    """Rough armchair shape under a sheet: seat, back, two arms (faces -X)."""
    parts = [hg.box(name + "_Seat", (0.75, 0.8, 0.42), (0, 0, 0.21 + 0.06), "WoodDark", coll, bevel=0.05)]
    parts.append(hg.box(name + "_Back", (0.2, 0.8, 0.95), (0.3, 0, 0.5), "WoodDark", coll, bevel=0.06))
    for k, y in enumerate((-0.35, 0.35)):
        parts.append(hg.box("%s_Arm%d" % (name, k), (0.7, 0.14, 0.65), (0.02, y, 0.33), "WoodDark", coll, bevel=0.05))
    return parts


def cabinet_proxy(name, coll):
    """Tall cabinet/hutch under a sheet with a shelf step (Basement_Fusebox, left)."""
    return [hg.box(name + "_Low", (0.55, 1.1, 0.8), (0, 0, 0.4), "WoodDark", coll, bevel=0.02),
            hg.box(name + "_High", (0.35, 1.05, 0.75), (0.1, 0, 1.17), "WoodDark", coll, bevel=0.02)]


def sheet_draped(name, coll, proxy_parts, sheet_size, height, legs=(), seed=1):
    """Drops a cloth over the proxy furniture with Blender's cloth simulation and keeps the result.
    The proxy is removed (only the legs passed in stay visible below the sheet)."""
    scene = bpy.context.scene
    for p in proxy_parts:
        bpy.context.view_layer.objects.active = p
        p.modifiers.new("Collision", "COLLISION")
        p.collision.thickness_outer = 0.01
    floor = hg.box(name + "_Floor", (6, 6, 0.02), (0, 0, -0.01), "Concrete", coll)
    floor.modifiers.new("Collision", "COLLISION")
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=56, y_subdivisions=56, size=1.0, location=(0, 0, height))
    sheet = bpy.context.active_object
    sheet.name = name + "_Cloth"
    sheet.scale = (sheet_size[0], sheet_size[1], 1)
    hg.apply_transforms(sheet)
    for c in sheet.users_collection:
        c.objects.unlink(sheet)
    coll.objects.link(sheet)
    rnd = random.Random(seed)
    for v in sheet.data.vertices:
        v.co.z += rnd.uniform(-0.01, 0.01)
    cloth = sheet.modifiers.new("Cloth", "CLOTH")
    cloth.settings.quality = 8
    cloth.settings.mass = 0.25
    cloth.settings.tension_stiffness = 12
    cloth.settings.compression_stiffness = 12
    cloth.settings.bending_stiffness = 0.4
    cloth.collision_settings.use_self_collision = True
    cloth.collision_settings.distance_min = 0.006
    cloth.point_cache.frame_start = 1
    cloth.point_cache.frame_end = 80
    scene.frame_start, scene.frame_end = 1, 80
    for f in range(1, 81):
        scene.frame_set(f)
    bpy.ops.object.select_all(action="DESELECT")
    sheet.select_set(True)
    bpy.context.view_layer.objects.active = sheet
    bpy.ops.object.modifier_apply(modifier="Cloth")
    scene.frame_set(1)
    solid = sheet.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.006
    smooth = sheet.modifiers.new("Smooth", "SMOOTH")
    smooth.iterations = 3
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Smooth")
    sheet.data.materials.clear()
    sheet.data.materials.append(hg.material("Sheet"))
    for p in list(proxy_parts) + [floor]:
        bpy.data.objects.remove(p)
    obj = hg.join([sheet] + list(legs), name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    hg.world_uv(obj)
    return obj


def sheet_armchair(name, coll):
    legs = [hg.cylinder("%s_Leg%d" % (name, i), 0.025, 0.1, (x, y, 0.05), "WoodDark", coll, segments=8, radius_top=0.02)
            for i, (x, y) in enumerate(((-0.33, -0.35), (-0.33, 0.35), (0.33, -0.35), (0.33, 0.35)))]
    return sheet_draped(name, coll, armchair_proxy(name + "_Proxy", coll), (2.3, 2.3), 1.2, legs, seed=2)


def sheet_cabinet(name, coll):
    return sheet_draped(name, coll, cabinet_proxy(name + "_Proxy", coll), (2.4, 2.9), 1.75, seed=3)


def wooden_chair(name, coll, seed=1):
    """Old wooden chair with a slatted back and stretchers (Basement_Fusebox, left). Faces -X."""
    parts = [hg.box(name + "_Seat", (0.42, 0.42, 0.035), (0, 0, 0.46), "WoodDark", coll, bevel=0.008)]
    for i, (x, y) in enumerate(((-0.18, -0.18), (-0.18, 0.18), (0.18, -0.18), (0.18, 0.18))):
        hgt = 0.95 if x > 0 else 0.45
        parts.append(hg.box("%s_Leg%d" % (name, i), (0.035, 0.035, hgt), (x, y, hgt / 2), "WoodDark", coll, bevel=0.005))
    for k, z in enumerate((0.62, 0.78, 0.92)):
        parts.append(hg.box("%s_Slat%d" % (name, k), (0.025, 0.36, 0.05 if k < 2 else 0.07), (0.18, 0, z), "WoodDark", coll, bevel=0.006))
    for i, (p0, p1) in enumerate((((-0.18, -0.18, 0.18), (0.18, -0.18, 0.18)), ((-0.18, 0.18, 0.18), (0.18, 0.18, 0.18)), ((-0.18, -0.18, 0.12), (-0.18, 0.18, 0.12)))):
        parts.append(hg.rod("%s_Str%d" % (name, i), p0, p1, 0.012, "WoodDark", coll, segments=6))
    obj = hg.join(parts, name)
    hg.jitter(obj, 0.002, seed=seed)
    hg.world_uv(obj)
    return obj


def puddle(name, coll, radius, seed):
    obj = blob(name, coll, radius, seed, "Water")
    hg.world_uv(obj)
    return obj


def wall_panel(name, coll, mat, size=(2.0, 0.2, 2.6)):
    """Straight wall piece along X, from X=0, the room side at Y=0 facing -Y (like the hallway walls)."""
    w, d, h = size
    obj = hg.box(name, (w, d, h), (w / 2, d / 2, h / 2), mat, coll)
    hg.world_uv(obj)
    return obj


def floor_tile(name, coll, mat, size=2.0, thickness=0.1):
    obj = hg.box(name, (size, size, thickness), (size / 2, size / 2, -thickness / 2), mat, coll)
    hg.world_uv(obj)
    return obj


# --- Secret basement -------------------------------------------------------------------------------

def crt_monitor(name, coll, size=0.42, screen="ScreenStatic"):
    """Beige computer CRT: square front with a bezel, tapered tube housing at the back, little stand.
    Screen faces -X (furniture convention), glass mapped 0..1."""
    s = size
    parts = [hg.box(name + "_Front", (0.08, s, s * 0.9), (-s * 0.4, 0, s * 0.5), "PlasticBeige", coll, bevel=0.025)]
    back = hg.box(name + "_Back", (s * 0.75, s * 0.8, s * 0.72), (0.0, 0, s * 0.5), "PlasticBeige", coll, bevel=0.04)
    for v in back.data.vertices:
        if v.co.x > 0:
            v.co.y *= 0.62
            v.co.z = (v.co.z) * 0.62 + 0.02
    parts.append(back)
    parts.append(hg.box(name + "_Bezel", (0.01, s * 0.84, s * 0.72), (-s * 0.4 - 0.042, 0, s * 0.53), "Bakelite", coll, bevel=0.012))
    glass = hg.box(name + "_Glass", (0.02, s * 0.74, s * 0.6), (-s * 0.4 - 0.05, 0, s * 0.53), screen, coll, bevel=0.015)
    for v in glass.data.vertices:
        if v.co.x < 0:
            v.co.x -= 0.012 * (1 - (v.co.y / (s * 0.37)) ** 2) * (1 - (v.co.z / (s * 0.3)) ** 2)
    hg.face_uv(glass, "yz")
    # face_uv runs along +Y; seen from -X that is right-to-left, so flip U.
    for loop in glass.data.uv_layers.active.data:
        loop.uv.x = 1 - loop.uv.x
    parts.append(glass)
    parts.append(hg.box(name + "_Chin", (0.02, s * 0.5, 0.04), (-s * 0.4 - 0.04, s * 0.15, s * 0.11), "PlasticBeige", coll))
    for k in range(2):
        parts.append(hg.cylinder("%s_Knob%d" % (name, k), 0.008, 0.012, (-s * 0.4 - 0.05, -s * 0.3 + k * 0.03, s * 0.11), "Bakelite", coll, segments=8, rotation=RY))
    parts.append(hg.box(name + "_Stand", (s * 0.5, s * 0.5, 0.04), (-0.02, 0, 0.02), "PlasticBeige", coll, bevel=0.01))
    for k in range(5):
        parts.append(hg.box("%s_Vent%d" % (name, k), (s * 0.3, 0.008, 0.01), (s * 0.08, -s * 0.28, s * 0.55 + k * 0.03), "Bakelite", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0, skip=("ScreenStatic", "ScreenTerminal", "ScreenWave", "ScreenAmber", "ScreenRecording"))
    return obj


def vcr(name, coll):
    """VHS video recorder: black box, cassette flap, green display, buttons. Front faces -X."""
    parts = [hg.box(name + "_Body", (0.32, 0.43, 0.09), (0, 0, 0.045), "VHS", coll, bevel=0.006)]
    parts.append(hg.box(name + "_Flap", (0.005, 0.2, 0.03), (-0.161, -0.06, 0.055), "MetalDark", coll))
    parts.append(hg.box(name + "_Display", (0.004, 0.08, 0.02), (-0.161, 0.12, 0.06), "LedGreen", coll))
    for k in range(5):
        parts.append(hg.box("%s_Btn%d" % (name, k), (0.008, 0.018, 0.01), (-0.163, 0.08 + k * 0.022, 0.025), "MetalPainted", coll, bevel=0.002))
    parts.append(hg.cylinder(name + "_Jog", 0.018, 0.01, (-0.163, 0.19, 0.045), "MetalPainted", coll, segments=12, rotation=RY))
    for k, y in enumerate((-0.18, 0.18)):
        parts.append(hg.box("%s_Foot%d" % (name, k), (0.25, 0.03, 0.008), (0, y, -0.004), "Rubber", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def vhs_parts(name, coll, loc, rot_z=0.0, standing=False):
    """One VHS tape (188 x 104 x 25 mm) with a paper label on the spine (+Y... spine faces -X)."""
    x, y, z = loc
    size = (0.104, 0.188, 0.025) if not standing else (0.104, 0.025, 0.188)
    tape = hg.box(name + "_Shell", size, (0, 0, size[2] / 2), "VHS", coll, bevel=0.002)
    label = hg.box(name + "_Label", (0.002, size[1] * 0.8, size[2] * 0.6), (-0.053, 0, size[2] / 2), "Label", coll)
    out = []
    for o in (tape, label):
        hg.rotate_about_z(o, rot_z)
        o.location.x += x
        o.location.y += y
        o.location.z += z
        out.append(o)
    return out


def vhs_tape(name, coll):
    obj = hg.join(vhs_parts(name, coll, (0, 0, 0)), name)
    hg.world_uv(obj, scale=4.0)
    return obj


def vhs_stack(name, coll, count=6, seed=1):
    rnd = random.Random(seed)
    parts = []
    for k in range(count):
        parts += vhs_parts("%s_T%d" % (name, k), coll, (rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), k * 0.0255), rnd.uniform(-0.12, 0.12))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def vhs_floor(name, coll, seed=4):
    """Tapes spilled on the floor: a toppled stack and loose ones, one leaning on its edge."""
    rnd = random.Random(seed)
    parts = []
    for k in range(4):
        parts += vhs_parts("%s_S%d" % (name, k), coll, (0, 0, k * 0.0255), rnd.uniform(-0.2, 0.2))
    for k in range(4):
        parts += vhs_parts("%s_L%d" % (name, k), coll, (rnd.uniform(-0.5, 0.5), rnd.uniform(0.2, 0.6), 0), rnd.uniform(0, math.pi))
    lean = vhs_parts(name + "_Lean", coll, (0.3, -0.25, 0), 0.3, standing=True)
    for o in lean:
        o.rotation_euler.x += math.radians(-25)
    parts += lean
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def old_desk(name, coll):
    """Worn computer desk (Secret_Basement): thick top with a chipped edge, pedestal with a drawer
    pulled out on the right, open on the left for VCR stacks. Faces -X."""
    d, w, h = 0.75, 1.6, 0.76
    parts = [hg.box(name + "_Top", (d, w, 0.05), (0, 0, h - 0.025), "WoodWorn", coll, bevel=0.012)]
    top = parts[0]
    hg.jitter(top, 0.004, seed=3)
    parts.append(hg.box(name + "_Ped", (d - 0.06, 0.42, h - 0.05), (0.02, w / 2 - 0.24, (h - 0.05) / 2), "WoodWorn", coll, bevel=0.008))
    parts.append(hg.box(name + "_DrawerBox", (0.3, 0.36, 0.12), (-d / 2 + 0.1, w / 2 - 0.24, h - 0.13), "WoodWorn", coll))
    parts.append(hg.box(name + "_DrawerFront", (0.02, 0.38, 0.14), (-d / 2 - 0.05, w / 2 - 0.24, h - 0.13), "WoodWorn", coll, bevel=0.004))
    parts.append(hg.box(name + "_Pull", (0.02, 0.1, 0.02), (-d / 2 - 0.065, w / 2 - 0.24, h - 0.13), "MetalDark", coll, bevel=0.004))
    for i, (x, y) in enumerate(((-d / 2 + 0.04, -w / 2 + 0.04), (d / 2 - 0.04, -w / 2 + 0.04))):
        parts.append(hg.box("%s_Leg%d" % (name, i), (0.05, 0.05, h - 0.05), (x, y, (h - 0.05) / 2), "WoodWorn", coll, bevel=0.006))
    parts.append(hg.box(name + "_Modesty", (0.02, w - 0.5, 0.35), (d / 2 - 0.03, -0.2, h - 0.25), "WoodWorn", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def mixer(name, coll, width=0.42, seed=1):
    """Grey control unit with knobs, two VU meters and a tiny screen (on the desk, under the CRTs).
    Front slopes to -X."""
    rnd = random.Random(seed)
    parts = [hg.box(name + "_Body", (0.28, width, 0.12), (0, 0, 0.06), "MetalPainted", coll, bevel=0.01)]
    face = hg.box(name + "_Face", (0.02, width - 0.02, 0.1), (-0.14, 0, 0.06), "MetalDark", coll)
    parts.append(face)
    for k in range(6):
        y = -width / 2 + 0.05 + k * (width - 0.18) / 5
        parts.append(hg.cylinder("%s_Knob%d" % (name, k), 0.013, 0.02, (-0.155, y, 0.04 + 0.04 * (k % 2)), "Bakelite", coll, segments=10, rotation=RY))
    for k in range(2):
        parts.append(hg.box("%s_Meter%d" % (name, k), (0.005, 0.05, 0.035), (-0.152, width / 2 - 0.13 + k * 0.06, 0.07), "Gauge", coll))
    parts.append(hg.box(name + "_Screen", (0.004, 0.06, 0.04), (-0.153, -width / 2 + 0.06, 0.08), "LedGreen", coll))
    for k in range(4):
        parts.append(hg.box("%s_Led%d" % (name, k), (0.006, 0.01, 0.01), (-0.153, -0.02 + k * 0.02, 0.105), rnd.choice(("LedRed", "LedGreen")), coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def keyboard(name, coll):
    """Beige 80s keyboard: wedge body with rows of keys. Keys face up, the near edge to -X."""
    parts = [hg.box(name + "_Body", (0.17, 0.46, 0.03), (0, 0, 0.015), "PlasticBeige", coll, bevel=0.006)]
    for r in range(5):
        for c in range(16):
            parts.append(hg.box("%s_K%d_%d" % (name, r, c), (0.018, 0.018, 0.01), (-0.06 + r * 0.025, -0.2 + c * 0.025, 0.035 + r * 0.002), "PlasticBeige", coll, bevel=0.002))
    parts.append(hg.box(name + "_Space", (0.018, 0.14, 0.01), (-0.083, -0.02, 0.034), "PlasticBeige", coll, bevel=0.002))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def mouse(name, coll):
    parts = [hg.sphere(name + "_Body", 0.05, (0, 0, 0.012), "PlasticBeige", coll, segments=14, rings=7, scale=(1.15, 0.65, 0.42))]
    parts.append(hg.cable(name + "_Cord", [(0.055, 0, 0.015), (0.12, 0.02, 0.006), (0.25, -0.05, 0.006), (0.4, 0.0, 0.006)], 0.003, "PlasticBeige", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def red_lamp(name, coll):
    """Two-arm desk lamp with a cone shade and a red bulb (Secret_Basement). Shade looks to -X."""
    base = (0, 0, 0)
    elbow = (0.08, 0, 0.42)
    head = (-0.12, 0, 0.62)
    parts = [hg.cylinder(name + "_Base", 0.09, 0.03, (0, 0, 0.015), "MetalDark", coll, segments=18)]
    parts.append(hg.rod(name + "_Arm1", (0, 0, 0.03), elbow, 0.01, "PaintRed", coll))
    parts.append(hg.rod(name + "_Arm2", elbow, head, 0.01, "PaintRed", coll))
    for p in ((0, 0, 0.03), elbow, head):
        parts.append(hg.sphere(name + "_Joint%.2f" % p[2], 0.018, p, "MetalDark", coll, segments=10, rings=5))
    shade = hg.cylinder(name + "_Shade", 0.11, 0.14, (head[0] - 0.05, 0, head[2] - 0.07), "MetalDark", coll, segments=20, radius_top=0.035)
    shade.rotation_euler.y = math.radians(-30)
    parts.append(shade)
    parts.append(hg.sphere(name + "_Bulb", 0.04, (head[0] - 0.08, 0, head[2] - 0.12), "BeaconRed", coll, segments=12, rings=6))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def office_chair(name, coll):
    """Worn office chair: five-star base with casters, gas lift, padded seat, backrest on a bent bar.
    Faces -X."""
    parts = []
    for k in range(5):
        a = k * 2 * math.pi / 5
        tip = (0.3 * math.cos(a), 0.3 * math.sin(a), 0.07)
        parts.append(hg.rod("%s_Spoke%d" % (name, k), (0, 0, 0.1), tip, 0.018, "MetalDark", coll))
        parts.append(hg.sphere("%s_Caster%d" % (name, k), 0.03, (tip[0], tip[1], 0.03), "Rubber", coll, segments=10, rings=5, scale=(1, 0.6, 1)))
        parts.append(hg.rod("%s_Fork%d" % (name, k), tip, (tip[0], tip[1], 0.03), 0.008, "MetalDark", coll, segments=6))
    parts.append(hg.cylinder(name + "_Hub", 0.045, 0.06, (0, 0, 0.1), "MetalDark", coll, segments=14))
    parts.append(hg.cylinder(name + "_Lift", 0.025, 0.3, (0, 0, 0.27), "MetalDark", coll, segments=12))
    parts.append(hg.box(name + "_SeatPlate", (0.25, 0.25, 0.03), (0, 0, 0.43), "MetalDark", coll))
    seat = hg.box(name + "_Seat", (0.46, 0.47, 0.08), (0, 0, 0.48), "Fabric", coll, bevel=0.035)
    hg.jitter(seat, 0.004, seed=5)
    parts.append(seat)
    parts.append(hg.rod(name + "_BarLow", (0.12, 0, 0.44), (0.27, 0, 0.47), 0.018, "MetalDark", coll))
    parts.append(hg.rod(name + "_BarUp", (0.27, 0, 0.47), (0.25, 0, 0.75), 0.018, "MetalDark", coll))
    back = hg.box(name + "_Back", (0.07, 0.42, 0.4), (0.24, 0, 0.88), "Fabric", coll, bevel=0.03)
    back.rotation_euler.y = math.radians(-8)
    hg.jitter(back, 0.004, seed=6)
    parts.append(back)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=2.0)
    return obj


def pc_tower(name, coll):
    parts = [hg.box(name + "_Case", (0.45, 0.19, 0.42), (0, 0, 0.21), "PlasticBeige", coll, bevel=0.01)]
    for k in range(2):
        parts.append(hg.box("%s_Bay%d" % (name, k), (0.005, 0.14, 0.04), (-0.226, 0, 0.35 - k * 0.05), "PlasticBeige", coll, bevel=0.003))
    parts.append(hg.box(name + "_Floppy", (0.005, 0.1, 0.004), (-0.229, 0, 0.35), "Bakelite", coll))
    parts.append(hg.box(name + "_Power", (0.008, 0.02, 0.02), (-0.228, 0.05, 0.12), "PlasticBeige", coll, bevel=0.003))
    parts.append(hg.box(name + "_Led", (0.004, 0.008, 0.008), (-0.228, 0.05, 0.16), "LedGreen", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def concrete_stairs(name, coll, rise=2.8, run=3.6, width=1.1, steps=14):
    """Narrow concrete stairs between two walls (Secret_Basement): solid flight, worn wooden handrail on
    brackets along the +Y wall. Pivot: bottom front corner; climbs along +X."""
    parts = []
    h, d = rise / steps, run / steps
    for i in range(steps):
        parts.append(hg.box("%s_Step%d" % (name, i), (d + 0.02, width, h * (i + 1)), (i * d + d / 2, width / 2, h * (i + 1) / 2), "Concrete", coll, bevel=0.01))
    rail_y = width - 0.06
    for k in range(4):
        x = 0.3 + k * (run - 0.6) / 3
        z = 0.95 + x / run * rise
        parts.append(hg.rod("%s_Bracket%d" % (name, k), (x, width, z - 0.05), (x, rail_y, z - 0.05), 0.008, "MetalDark", coll, segments=6))
    parts.append(hg.rod(name + "_Rail", (0.1, rail_y, 0.9), (run, rail_y, 0.9 + rise), 0.025, "WoodWorn", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def junction_box(name, coll):
    """Grey junction box high on the wall with a bundle of coloured cables drooping out (Secret_Basement,
    top right). Back at Y=0, faces -Y."""
    rnd = random.Random(41)
    parts = [hg.box(name + "_Box", (0.22, 0.1, 0.32), (0, -0.05, 0), "MetalPainted", coll, bevel=0.012)]
    parts.append(hg.box(name + "_Lid", (0.2, 0.01, 0.3), (0, -0.104, 0), "MetalPainted", coll, bevel=0.006))
    for k in range(6):
        y = -0.04 - k * 0.008
        start = (0.11, y, 0.1 - k * 0.03)
        pts = [start, (0.3 + rnd.uniform(0, 0.1), y - 0.02, 0.12 - k * 0.02), (0.6 + k * 0.05, y - 0.03, -0.05 - rnd.uniform(0, 0.15)),
               (1.0 + k * 0.08, y - 0.02, 0.15 - k * 0.03)]
        parts.append(hg.cable("%s_C%d" % (name, k), pts, 0.008, ("Cable", "CableRed", "CableGreen", "Cable", "PaintYellow", "PaintBlue")[k], coll))
    for k in range(3):
        parts.append(hg.cable("%s_Down%d" % (name, k), [(-0.05 + k * 0.05, -0.05, -0.16), (-0.05 + k * 0.05, -0.04, -0.6), (-0.02 + k * 0.05, -0.03, -1.4)], 0.01, "Cable", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=3.0)
    return obj


def light_switch(name, coll):
    parts = [hg.box(name + "_Plate", (0.08, 0.012, 0.12), (0, -0.006, 0), "PlasticBeige", coll, bevel=0.004)]
    parts.append(hg.box(name + "_Toggle", (0.012, 0.02, 0.03), (0, -0.02, 0.006), "PlasticBeige", coll, bevel=0.003))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Basement")
    assets = [
        # Fuse basement.
        fuse_box("SM_FuseBox", coll),
        fuse_box_door("SM_FuseBox_Door", coll),
        fuse("SM_Fuse", coll),
        knife_switch("SM_KnifeSwitch", coll),
        knife_switch_lever("SM_KnifeSwitch_Lever", coll),
        pipe("SM_Pipe_200", coll),
        pipe_elbow("SM_Pipe_Elbow", coll),
        ceiling_pipes("SM_Pipes_Ceiling_400", coll),
        water_heater("SM_WaterHeater", coll),
        sheet_armchair("SM_Sheet_Armchair", coll),
        sheet_cabinet("SM_Sheet_Cabinet", coll),
        wooden_chair("SM_Chair_Wood_Old", coll),
        puddle("SM_Puddle_Large", coll, 0.6, seed=1),
        puddle("SM_Puddle_Small", coll, 0.25, seed=2),
        wall_panel("SM_Wall_Brick_200", coll, "Brick"),
        wall_panel("SM_Wall_Concrete_200", coll, "Concrete"),
        floor_tile("SM_Floor_Concrete_200", coll, "Concrete"),
        # Secret basement.
        crt_monitor("SM_CRT_Monitor", coll),
        crt_monitor("SM_CRT_Monitor_Large", coll, size=0.52),
        crt_monitor("SM_CRT_Monitor_Recording", coll, size=0.52, screen="ScreenRecording"),
        vcr("SM_VCR", coll),
        vhs_tape("SM_VHS_Tape", coll),
        vhs_stack("SM_VHS_Stack", coll),
        vhs_floor("SM_VHS_Floor", coll),
        old_desk("SM_Desk_Old", coll),
        mixer("SM_Mixer", coll),
        keyboard("SM_Keyboard_Old", coll),
        mouse("SM_Mouse_Old", coll),
        red_lamp("SM_DeskLamp_Red", coll),
        office_chair("SM_OfficeChair", coll),
        pc_tower("SM_PC_Tower", coll),
        concrete_stairs("SM_Stairs_Concrete", coll),
        junction_box("SM_JunctionBox", coll),
        light_switch("SM_LightSwitch", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x
        x += max(obj.dimensions.x, 0.4) + 0.6
    hg.save_blend(os.path.join(OUT, "Basement_Kit.blend"))
    print("exported %d basement assets to %s" % (len(assets), OUT))


build()
