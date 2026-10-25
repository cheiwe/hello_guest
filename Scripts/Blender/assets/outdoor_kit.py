"""
Outdoors (Street_Example, Yard_01-03, Ufo_above_the_roof): the rusty van with a real side-door
opening and a separate sliding door (the Guest drags the neighbour into it), gnarled oaks, a street
tree, a dead tree, bushes, a hedge, grass tufts, the UFO with its tractor beam, the ray gun, and
street pieces (road with a double yellow line, curb, sidewalk) and a mailbox.

Vehicles and the gun point +X (like the characters). Trees grow from the origin.
"""

import importlib
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

OUT = os.path.join(hg.MODELS_DIR, "Outdoor")
RX = (math.radians(90), 0, 0)
RY = (0, math.radians(90), 0)


def lathe(name, profile, coll, mat, segments=48):
    """Surface of revolution around Z from a (radius, z) profile, top to bottom or bottom to top."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = [bm.verts.new((r * math.cos(2 * math.pi * k / segments), r * math.sin(2 * math.pi * k / segments), z)) for k in range(segments)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(segments):
            bm.faces.new((a[k], a[(k + 1) % segments], b[(k + 1) % segments], b[k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material(mat))
    coll.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def blob(name, coll, radius, loc, mat, seed, squash=(1, 1, 1), detail=0.35, level=3):
    """Lumpy cartoon foliage/bush mass: an icosphere pushed about by noise."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=level, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.scale = squash
    tex = bpy.data.textures.new(name + "_N", "CLOUDS")
    tex.noise_scale = radius * 0.45
    tex.noise_depth = 1
    disp = obj.modifiers.new("D", "DISPLACE")
    disp.texture = tex
    disp.strength = radius * detail
    disp.texture_coords = "GLOBAL"
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="D")
    bpy.data.textures.remove(tex)
    obj.data.materials.append(hg.material(mat))
    for p in obj.data.polygons:
        p.use_smooth = True
    rnd = random.Random(seed)
    obj.rotation_euler = (rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0, 6))
    return obj


# --- Van ---------------------------------------------------------------------------------------------

VAN_L, VAN_W, VAN_Z0, VAN_Z1 = 4.3, 1.72, 0.32, 1.95
DOOR_X0, DOOR_X1 = -0.35, 0.85          # side door opening on the -Y side (= +Y, right side in Unreal)


def rounded_box(name, size, loc, mat, coll, bevel, segments=5):
    """Box with soft, many-segment rounded edges and smooth shading (car body panels)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segments, affect="EDGES", profile=0.5)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(hg.material(mat))
    coll.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def shape_van_body(obj, x_offset):
    """Bends a body block into the bus shape: crowned roof, bulging nose, windscreen leaning back."""
    for v in obj.data.vertices:
        x, y, z = v.co.x + x_offset, v.co.y, v.co.z + obj.location.z
        t = min(abs(y) / (VAN_W / 2), 1.0)
        if z > VAN_Z1 - 0.5:
            v.co.z -= 0.12 * t ** 2 * (z - (VAN_Z1 - 0.5)) / 0.5
        if x > VAN_L / 2 - 0.5:
            f = (x - (VAN_L / 2 - 0.5)) / 0.5
            v.co.x += 0.1 * f * (1 - t ** 2)
            if z > 1.15:
                v.co.x -= 0.22 * (z - 1.15) / (VAN_Z1 - 1.15) * f


def van(name, coll):
    """Rusty split-window bus: rounded body built from blocks around the side-door opening, split
    windshield, V front panel, round badge (no make), headlights, bumpers, wheels in dark arches,
    windows all round, engine louvres at the back, a dark interior behind the opening."""
    parts = []
    h = VAN_Z1 - VAN_Z0
    zc = VAN_Z0 + h / 2
    # One rounded body; the side-door opening is cut out with a boolean, which leaves the hollow
    # interior behind it (the far side wall stays 10 cm thick).
    body = rounded_box(name + "_Body", (VAN_L, VAN_W, h), (0, 0, zc), "VanPaint", coll, 0.38)
    shape_van_body(body, 0.0)
    cutter = hg.box(name + "_Cut", (DOOR_X1 - DOOR_X0, VAN_W, VAN_Z1 - VAN_Z0 - 0.42), ((DOOR_X0 + DOOR_X1) / 2, -0.1, VAN_Z0 + 0.15 + (VAN_Z1 - VAN_Z0 - 0.42) / 2), "VanInterior", coll)
    hole = hg.box(name + "_Cut2", (DOOR_X1 - DOOR_X0 + 0.7, VAN_W - 0.24, VAN_Z1 - VAN_Z0 - 0.3), ((DOOR_X0 + DOOR_X1) / 2 - 0.35, 0.0, VAN_Z0 + 0.1 + (VAN_Z1 - VAN_Z0 - 0.3) / 2), "VanInterior", coll)
    for c in (cutter, hole):
        mod = body.modifiers.new("Cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = c
        mod.solver = "EXACT"
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(c)
    parts.append(body)
    mid = ((DOOR_X0 + DOOR_X1) / 2, DOOR_X1 - DOOR_X0)
    # Interior seen through the opening.
    parts.append(hg.box(name + "_Floor", (DOOR_X1 - DOOR_X0, VAN_W - 0.1, 0.03), (mid[0], 0, VAN_Z0 + 0.15), "VanInterior", coll))
    parts.append(hg.box(name + "_Bench", (0.45, VAN_W - 0.2, 0.4), (DOOR_X0 + 0.25, 0.0, VAN_Z0 + 0.35), "VanInterior", coll, bevel=0.04))

    fx = VAN_L / 2
    # Split windshield on the leaning upper nose.
    lean = math.atan2(0.22, VAN_Z1 - 1.15)
    for k, y in enumerate((-0.36, 0.36)):
        wnd = hg.box("%s_Wind%d" % (name, k), (0.02, 0.58, 0.4), (fx + 0.005, y, 1.45), "VanGlass", coll, bevel=0.05)
        wnd.rotation_euler.y = -lean
        parts.append(wnd)
    post = hg.box(name + "_WindPost", (0.04, 0.07, 0.44), (fx + 0.015, 0, 1.45), "VanCream", coll)
    post.rotation_euler.y = -lean
    parts.append(post)
    # V-shaped front panel and badge.
    for k, sgn in enumerate((-1, 1)):
        v = hg.box("%s_VPanel%d" % (name, k), (0.02, 0.95, 0.09), (fx + 0.002, sgn * 0.38, 1.0), "VanCream", coll)
        v.rotation_euler.x = math.radians(sgn * 28)
        parts.append(v)
    parts.append(hg.cylinder(name + "_Badge", 0.12, 0.03, (fx + 0.01, 0, 0.95), "Chrome", coll, segments=24, rotation=RY))
    parts.append(hg.cylinder(name + "_BadgeIn", 0.09, 0.01, (fx + 0.03, 0, 0.95), "VanPaint", coll, segments=24, rotation=RY))
    for k, y in enumerate((-0.6, 0.6)):
        parts.append(hg.cylinder("%s_LampRim%d" % (name, k), 0.1, 0.05, (fx, y, 0.82), "Chrome", coll, segments=20, rotation=RY))
        parts.append(hg.sphere("%s_Lamp%d" % (name, k), 0.085, (fx + 0.02, y, 0.82), "Glass", coll, segments=14, rings=7, scale=(0.4, 1, 1)))
        parts.append(hg.sphere("%s_Signal%d" % (name, k), 0.035, (fx + 0.01, y * 1.05, 1.08), "PaintYellow", coll, segments=10, rings=5, scale=(0.5, 1, 1)))
    for k, x in enumerate((fx + 0.06, -fx - 0.06)):
        parts.append(hg.box("%s_Bumper%d" % (name, k), (0.08, VAN_W + 0.08, 0.1), (x, 0, 0.5), "ChromeRust", coll, bevel=0.03))
    # Windows: cab doors, three on each side of the rear block, rear window.
    for side in (-1, 1):
        y = side * (VAN_W / 2 + 0.005)
        parts.append(hg.box("%s_CabWin%d" % (name, side), (0.6, 0.02, 0.38), (1.45, y, 1.42), "VanGlass", coll, bevel=0.05))
        for k in range(3):
            x = -1.85 + k * 0.52
            parts.append(hg.box("%s_SideWin%d_%d" % (name, side, k), (0.44, 0.02, 0.36), (x, y, 1.45), "VanGlass", coll, bevel=0.05))
        # Cream belt line round the body.
        parts.append(hg.box("%s_Belt%d" % (name, side), (VAN_L - 0.4, 0.015, 0.05), (0, y, 1.2), "VanCream", coll))
        if side > 0:
            parts.append(hg.box(name + "_FarWin", (0.9, 0.02, 0.36), (mid[0], y, 1.45), "VanGlass", coll, bevel=0.05))
        parts.append(hg.box("%s_CabHandle%d" % (name, side), (0.12, 0.03, 0.025), (1.15, y + side * 0.01, 1.18), "Chrome", coll, bevel=0.01))
    parts.append(hg.box(name + "_RearWin", (0.02, 1.0, 0.3), (-fx - 0.005, 0, 1.5), "VanGlass", coll, bevel=0.05))
    for k in range(6):
        parts.append(hg.box("%s_Louvre%d" % (name, k), (0.02, 0.9, 0.025), (-fx - 0.005, 0, 0.75 + k * 0.05), "MetalDark", coll))
    for k, y in enumerate((-0.7, 0.7)):
        parts.append(hg.box("%s_Tail%d" % (name, k), (0.03, 0.08, 0.14), (-fx - 0.01, y, 0.95), "LedRed", coll, bevel=0.02))
    # Wheels in dark arches.
    for k, (x, sgn) in enumerate(((1.35, -1), (1.35, 1), (-1.4, -1), (-1.4, 1))):
        parts.append(hg.cylinder("%s_Arch%d" % (name, k), 0.43, 0.04, (x, sgn * (VAN_W / 2 - 0.01), 0.42), "MetalDark", coll, segments=24, rotation=RX))
        parts.append(hg.cylinder("%s_Tire%d" % (name, k), 0.36, 0.2, (x, sgn * (VAN_W / 2 - 0.1), 0.36), "Rubber", coll, segments=24, rotation=RX))
        parts.append(hg.cylinder("%s_Hub%d" % (name, k), 0.2, 0.04, (x, sgn * (VAN_W / 2 + 0.01), 0.36), "ChromeRust", coll, segments=20, rotation=RX))
        parts.append(hg.sphere("%s_HubCap%d" % (name, k), 0.08, (x, sgn * (VAN_W / 2 + 0.03), 0.36), "Chrome", coll, segments=12, rings=6, scale=(1, 0.4, 1)))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def van_side_door(name, coll):
    """Sliding door of the van. Pivot: its front bottom corner; it slides open along -X by 1.2 m.
    Socket on SM_Van: (0.85, -0.86, 0.39)."""
    w = DOOR_X1 - DOOR_X0
    h = VAN_Z1 - VAN_Z0 - 0.3
    parts = [hg.box(name + "_Panel", (w, 0.05, h), (-w / 2, 0, h / 2), "VanPaint", coll, bevel=0.025)]
    parts.append(hg.box(name + "_Win", (w - 0.25, 0.02, 0.36), (-w / 2, -0.03, h - 0.27), "VanGlass", coll, bevel=0.05))
    parts.append(hg.box(name + "_Belt", (w, 0.015, 0.05), (-w / 2, -0.03, 1.2 - VAN_Z0 - 0.07), "VanCream", coll))
    parts.append(hg.box(name + "_Handle", (0.14, 0.03, 0.03), (-0.15, -0.045, h * 0.55), "Chrome", coll, bevel=0.01))
    for k, z in enumerate((0.05, h - 0.03)):
        parts.append(hg.box("%s_Rail%d" % (name, k), (w, 0.02, 0.025), (-w / 2, 0.035, z), "MetalDark", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


# --- Trees and plants --------------------------------------------------------------------------------

def grow(name, coll, parts, tips, start, direction, length, radius, depth, rnd, twist=0.35):
    """One gnarled branch as a tapered tube along a wobbly path, then 2-3 children from its end."""
    d = Vector(direction).normalized()
    pts = [Vector(start)]
    n = 5
    for i in range(1, n + 1):
        wob = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.5))) * twist
        d = (d + wob * 0.5).normalized()
        pts.append(pts[-1] + d * (length / n))
    radii = [1.0 - 0.45 * i / n for i in range(n + 1)]
    parts.append(hg.cable("%s_%d_%d" % (name, depth, len(parts)), [tuple(p) for p in pts], radius, "Bark", coll, segments=10, resolution=4, radii=radii))
    end = pts[-1]
    if depth <= 1:
        tips.append((end, radius))
    if depth == 0:
        return
    for k in range(rnd.choice((2, 2, 3))):
        side = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)).normalized()
        child = (d * 0.8 + side * rnd.uniform(0.5, 1.0) + Vector((0, 0, rnd.uniform(0.1, 0.5)))).normalized()
        grow(name, coll, parts, tips, end, child, length * rnd.uniform(0.65, 0.85), radius * 0.58, depth - 1, rnd, twist)


def tree(name, coll, seed, height=2.4, radius=0.5, depth=3, canopy=1.35, leaves=True, twist=0.45, spread=1.5, rise=(0.25, 0.6)):
    """Cartoon oak: flared roots, a bent trunk splitting into gnarled limbs, lumpy leaf masses at the
    branch tips (none for the dead tree)."""
    rnd = random.Random(seed)
    parts, tips = [], []
    trunk_top = Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), height))
    mid = Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), height * 0.5))
    parts.append(hg.cable(name + "_Trunk", [(0, 0, -0.1), (0, 0, 0.4), tuple(mid), tuple(trunk_top)], radius, "Bark", coll, segments=12, resolution=6, radii=[1.25, 1.0, 0.85, 0.7]))
    for k in range(5):
        a = k * 2 * math.pi / 5 + rnd.uniform(-0.3, 0.3)
        out = Vector((math.cos(a), math.sin(a), 0))
        parts.append(hg.cable("%s_Root%d" % (name, k), [tuple(out * radius * 0.3 + Vector((0, 0, 0.5))), tuple(out * radius * 1.3 + Vector((0, 0, 0.1))), tuple(out * radius * 2.4 + Vector((0, 0, -0.08)))],
                              radius * 0.4, "Bark", coll, segments=8, resolution=4, radii=[1.0, 0.7, 0.3]))
    for k in range(rnd.choice((3, 4))):
        a = k * 2 * math.pi / 4 + rnd.uniform(-0.5, 0.5)
        dirv = Vector((math.cos(a) * spread, math.sin(a) * spread, rnd.uniform(*rise)))
        grow(name, coll, parts, tips, trunk_top, dirv, height * rnd.uniform(0.75, 0.95), radius * 0.62, depth - 1, rnd, twist)
    if leaves:
        for i, (p, r) in enumerate(tips):
            size = canopy * rnd.uniform(0.7, 1.05)
            parts.append(blob("%s_Leaves%d" % (name, i), coll, size, tuple(p + Vector((0, 0, size * 0.25))), rnd.choice(("Foliage", "Foliage", "FoliageDark")), seed * 31 + i,
                              squash=(1.0, 1.0, 0.62)))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def bush(name, coll, seed, size=0.8, lumps=5):
    rnd = random.Random(seed)
    parts = []
    for i in range(lumps):
        r = size * rnd.uniform(0.5, 0.8)
        parts.append(blob("%s_L%d" % (name, i), coll, r, (rnd.uniform(-size, size) * 0.7, rnd.uniform(-size, size) * 0.7, r * 0.6), rnd.choice(("Foliage", "FoliageDark")), seed * 7 + i,
                          squash=(1, 1, 0.8), level=2))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def hedge(name, coll, length=2.0, seed=3):
    """Trimmed hedge along X, from X=0, 0.7 m wide and 1.1 m high, lumpy surface."""
    parts = []
    rnd = random.Random(seed)
    k = 0
    x = 0.3
    while x < length - 0.2:
        parts.append(blob("%s_H%d" % (name, k), coll, 0.5, (x, rnd.uniform(-0.05, 0.05), 0.6), "Foliage", seed + k, squash=(1.0, 0.75, 1.15), detail=0.25, level=2))
        x += 0.45
        k += 1
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def grass_tuft(name, coll, seed, blades=26, height=0.45):
    """Clump of long grass blades (thin tapered triangles, two-sided masked material)."""
    rnd = random.Random(seed)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for i in range(blades):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0, 0.12)
        base = Vector((r * math.cos(a), r * math.sin(a), 0))
        lean = Vector((math.cos(a), math.sin(a), 0)) * rnd.uniform(0.05, 0.25)
        hgt = height * rnd.uniform(0.5, 1.1)
        side = Vector((-math.sin(a), math.cos(a), 0)) * 0.012
        mid = base + lean * 0.4 + Vector((0, 0, hgt * 0.55))
        tip = base + lean + Vector((0, 0, hgt))
        v = [bm.verts.new(p) for p in (base - side, base + side, mid + side * 0.6, mid - side * 0.6, tip)]
        bm.faces.new((v[0], v[1], v[2], v[3]))
        bm.faces.new((v[3], v[2], v[4]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material("Grass"))
    coll.objects.link(obj)
    hg.world_uv(obj)
    return obj


# --- UFO and ray gun ---------------------------------------------------------------------------------

def ufo(name, coll, r=6.0):
    """Riveted saucer (Ufo_above_the_roof): dome, upper hull with radial panel seams and glowing
    portholes, thick rim, lower hull with a ring of machinery boxes and pipes around the big green
    emitter. Pivot at the centre of the emitter."""
    parts = []
    upper = [(0.0, 2.85), (r * 0.1, 2.8), (r * 0.18, 2.55), (r * 0.24, 2.1), (r * 0.3, 1.9), (r * 0.36, 1.55), (r * 0.6, 1.2), (r * 0.85, 0.75), (r, 0.45)]
    parts.append(lathe(name + "_Upper", upper, coll, "UfoHull"))
    rim = [(r, 0.45), (r * 1.02, 0.35), (r * 1.02, 0.15), (r, 0.05)]
    parts.append(lathe(name + "_Rim", rim, coll, "UfoHullDark"))
    lower = [(r, 0.05), (r * 0.75, -0.25), (r * 0.5, -0.45), (r * 0.42, -0.5), (r * 0.42, -0.85), (r * 0.3, -0.95), (r * 0.27, -0.75), (r * 0.2, -0.7)]
    parts.append(lathe(name + "_Lower", lower, coll, "UfoHull"))
    parts.append(lathe(name + "_Emitter", [(r * 0.2, -0.7), (r * 0.12, -0.74), (0.0, -0.76)], coll, "UfoBeamGlow"))
    parts.append(hg.torus(name + "_EmitterRing", r * 0.2, 0.12, (0, 0, -0.72), "UfoHullDark", coll, segments=40, ring_segments=8))
    rnd = random.Random(5)
    # Radial seams on the upper hull and rivets along the rim.
    for k in range(16):
        a = 2 * math.pi * k / 16
        p0 = Vector((math.cos(a) * r * 0.38, math.sin(a) * r * 0.38, 1.52))
        p1 = Vector((math.cos(a) * r * 0.98, math.sin(a) * r * 0.98, 0.48))
        parts.append(hg.rod("%s_Seam%d" % (name, k), tuple(p0), tuple(p1), 0.035, "UfoHullDark", coll, segments=6))
    for k in range(12):
        a = 2 * math.pi * (k + 0.5) / 12
        c = Vector((math.cos(a) * r * 0.72, math.sin(a) * r * 0.72, 1.02))
        tilt = math.atan2(0.45, r * 0.25)
        rim_o = hg.torus("%s_PortRim%d" % (name, k), 0.32, 0.07, tuple(c), "UfoHullDark", coll, segments=20, ring_segments=6)
        glass = hg.cylinder("%s_Port%d" % (name, k), 0.3, 0.06, tuple(c), "UfoLight", coll, segments=20)
        for o in (rim_o, glass):
            o.rotation_euler = (0, tilt, a)
        parts += [rim_o, glass]
    for k in range(24):
        a = 2 * math.pi * k / 24
        parts.append(hg.sphere("%s_RimLight%d" % (name, k), 0.12, (math.cos(a) * r * 1.025, math.sin(a) * r * 1.025, 0.25), "UfoLight" if k % 2 else "UfoHullDark", coll, segments=10, rings=5))
    # Underside (what the player sees): big round lights on the outer ring, radial seams, vents.
    lower_tilt = math.atan2(0.3, r * 0.25)
    for k in range(10):
        a = 2 * math.pi * (k + 0.25) / 10
        c = Vector((math.cos(a) * r * 0.86, math.sin(a) * r * 0.86, -0.13))
        rim_o = hg.torus("%s_UnderRim%d" % (name, k), 0.42, 0.08, tuple(c), "UfoHullDark", coll, segments=20, ring_segments=6)
        lamp = hg.cylinder("%s_UnderLamp%d" % (name, k), 0.4, 0.08, tuple(c), "UfoLight", coll, segments=20)
        for o in (rim_o, lamp):
            o.rotation_euler = (0, -lower_tilt, a)
        parts += [rim_o, lamp]
    for k in range(20):
        a = 2 * math.pi * k / 20
        p0 = Vector((math.cos(a) * r * 0.99, math.sin(a) * r * 0.99, 0.03))
        p1 = Vector((math.cos(a) * r * 0.52, math.sin(a) * r * 0.52, -0.43))
        parts.append(hg.rod("%s_USeam%d" % (name, k), tuple(p0), tuple(p1), 0.03, "UfoHullDark", coll, segments=6))
    for k in range(6):
        a = 2 * math.pi * (k + 0.6) / 6
        c = Vector((math.cos(a) * r * 0.66, math.sin(a) * r * 0.66, -0.19))
        vent = hg.box("%s_Vent%d" % (name, k), (0.5, 0.9, 0.08), tuple(c), "MetalDark", coll, rotation=(0, -lower_tilt, a))
        parts.append(vent)
    # Machinery around the lower ring.
    for k in range(14):
        a = 2 * math.pi * k / 14 + rnd.uniform(-0.05, 0.05)
        c = Vector((math.cos(a) * r * 0.47, math.sin(a) * r * 0.47, -0.55))
        bx = hg.box("%s_Mach%d" % (name, k), (rnd.uniform(0.4, 0.7), rnd.uniform(0.5, 0.9), rnd.uniform(0.35, 0.55)), tuple(c), "UfoHullDark", coll, bevel=0.04)
        bx.rotation_euler.z = a
        parts.append(bx)
        if k % 3 == 0:
            parts.append(hg.box("%s_MachLight%d" % (name, k), (0.12, 0.25, 0.08), tuple(c + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0))), "UfoLight", coll, rotation=(0, 0, a)))
    pipe_pts = [(math.cos(2 * math.pi * t / 16) * r * 0.44, math.sin(2 * math.pi * t / 16) * r * 0.44, -0.8) for t in range(17)]
    parts.append(hg.cable(name + "_Pipe", pipe_pts, 0.09, "UfoHullDark", coll, segments=8, resolution=3))
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=0.5)
    return obj


def ufo_beam(name, coll, top=1.25, bottom=3.2, length=9.0):
    """Tractor beam: open cone hanging from the emitter (pivot at its top), additive translucent,
    the gradient texture fades it out towards the ground."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    seg = 40
    rings = []
    for z, r in ((0.0, top), (-length, bottom)):
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for k in range(seg):
        bm.faces.new((rings[0][k], rings[0][(k + 1) % seg], rings[1][(k + 1) % seg], rings[1][k]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material("Beam"))
    coll.objects.link(obj)
    uv = obj.data.uv_layers.new(name="UVMap").data
    for poly in obj.data.polygons:
        for li in poly.loop_indices:
            v = obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv[li].uv = ((math.atan2(v.y, v.x) / (2 * math.pi)) % 1.0 * 4, 1 + v.z / length)
    return obj


def ray_gun(name, coll):
    """Retro ray gun (Ufo_above_the_roof): bulbous body, pistol grip, tail fin, three glowing rings
    on the barrel, glass bubble at the muzzle, knobbed rear coil. Points +X, pivot at the grip."""
    parts = [hg.sphere(name + "_Body", 0.07, (0.0, 0, 0.12), "RayGunMetal", coll, segments=20, rings=10, scale=(1.35, 0.85, 0.9))]
    parts.append(hg.cylinder(name + "_Neck", 0.04, 0.08, (0.11, 0, 0.12), "RayGunMetal", coll, segments=16, rotation=RY, radius_top=0.028))
    parts.append(hg.cylinder(name + "_Barrel", 0.016, 0.18, (0.22, 0, 0.12), "Chrome", coll, segments=12, rotation=RY))
    for k, (x, mat) in enumerate(((0.17, "RingYellow"), (0.22, "RingPink"), (0.27, "RingGreen"))):
        parts.append(hg.torus("%s_Ring%d" % (name, k), 0.045 - k * 0.004, 0.006, (x, 0, 0.12), mat, coll, rotation=RY, segments=24, ring_segments=6))
    parts.append(hg.sphere(name + "_Bubble", 0.035, (0.335, 0, 0.12), "BulbGlass", coll, segments=16, rings=8))
    parts.append(hg.cylinder(name + "_Coil", 0.03, 0.06, (-0.1, 0, 0.12), "RayGunMetal", coll, segments=14, rotation=RY))
    for k in range(3):
        parts.append(hg.torus("%s_CoilRing%d" % (name, k), 0.034, 0.005, (-0.08 - k * 0.02, 0, 0.12), "RingPink", coll, rotation=RY, segments=16, ring_segments=4))
    parts.append(hg.sphere(name + "_Knob", 0.022, (-0.14, 0, 0.12), "PaintRed", coll, segments=10, rings=5))
    for k, y in enumerate((-0.06, 0.06)):
        parts.append(hg.sphere("%s_Dial%d" % (name, k), 0.02, (0.0, y, 0.13), "Chrome", coll, segments=10, rings=5, scale=(1, 0.4, 1)))
    grip = hg.box(name + "_Grip", (0.045, 0.035, 0.12), (-0.02, 0, 0.04), "Bakelite", coll, bevel=0.015)
    grip.rotation_euler.y = math.radians(-18)
    parts.append(grip)
    parts.append(hg.torus(name + "_Guard", 0.03, 0.005, (0.025, 0, 0.055), "RayGunMetal", coll, rotation=RX, segments=14, ring_segments=4))
    fin = hg.box(name + "_Fin", (0.08, 0.006, 0.06), (-0.04, 0, 0.19), "PaintRed", coll, bevel=0.003)
    for v in fin.data.vertices:
        if v.co.z > 0:
            v.co.x -= 0.03
    parts.append(fin)
    obj = hg.join(parts, name)
    hg.world_uv(obj, scale=4.0)
    return obj


# --- Street ------------------------------------------------------------------------------------------

def road(name, coll, length=4.0, width=7.0):
    """Asphalt road piece along X (from X=0), centred on Y, top at Z=0, with a double yellow line
    and a slightly worn surface."""
    parts = [hg.box(name + "_Asphalt", (length, width, 0.1), (length / 2, 0, -0.05), "Asphalt", coll)]
    for k, y in enumerate((-0.08, 0.08)):
        parts.append(hg.box("%s_Line%d" % (name, k), (length, 0.1, 0.004), (length / 2, y, 0.002), "RoadLine", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def curb(name, coll, length=4.0):
    """Concrete curb along X (from X=0): road side at Y=0, 15 cm above the road, rounded top edge."""
    obj = hg.box(name, (length, 0.18, 0.3), (length / 2, 0.09, 0.0), "Concrete", coll, bevel=0.03)
    hg.world_uv(obj)
    return obj


def sidewalk(name, coll, length=4.0, width=1.8, seed=7):
    """Sidewalk of 1 m concrete slabs with joints, one slab tilted and cracked, top at Z=0.15."""
    rnd = random.Random(seed)
    parts = []
    for i in range(int(length)):
        tilt = (rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02)) if i == 2 else (0, 0)
        s = hg.box("%s_Slab%d" % (name, i), (0.98, width, 0.12), (i + 0.5, width / 2, 0.09), "Concrete", coll, bevel=0.01, rotation=(tilt[0], tilt[1], 0))
        hg.jitter(s, 0.002, seed=i)
        parts.append(s)
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def mailbox(name, coll):
    """Rural mailbox on a wooden post: rounded tin box, red flag."""
    parts = [hg.box(name + "_Post", (0.1, 0.1, 1.1), (0, 0, 0.55), "WoodWeathered", coll, bevel=0.01)]
    parts.append(hg.box(name + "_Base", (0.5, 0.22, 0.03), (0.05, 0, 1.1), "WoodWeathered", coll))
    parts.append(hg.box(name + "_Box", (0.48, 0.2, 0.14), (0.05, 0, 1.19), "MetalPainted", coll, bevel=0.01))
    parts.append(hg.cylinder(name + "_Top", 0.1, 0.48, (0.05, 0, 1.26), "MetalPainted", coll, segments=16, rotation=RY))
    parts.append(hg.box(name + "_FlagArm", (0.02, 0.01, 0.2), (0.12, -0.11, 1.32), "PaintRed", coll))
    parts.append(hg.box(name + "_Flag", (0.08, 0.01, 0.06), (0.16, -0.11, 1.39), "PaintRed", coll))
    obj = hg.join(parts, name)
    hg.world_uv(obj)
    return obj


def rain_curtains(name, coll, size=10.0, height=14.0, rows=4):
    """Rain tile: a grid of vertical planes (along X and along Y) covering size x size m from the origin,
    for the additive, panning rain material. U runs 1 per 2 m, V 1 per 4 m of height."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for k in range(rows):
        c = (k + 0.5) * size / rows
        for along_x in (True, False):
            corners = [(0, 0), (size, 0), (size, height), (0, height)]
            verts = []
            for a, z in corners:
                verts.append(bm.verts.new((a, c, z) if along_x else (c, a, z)))
            face = bm.faces.new(verts)
            for loop, (a, z) in zip(face.loops, corners):
                loop[uv_layer].uv = (a / 2.0 + k * 0.37, z / 4.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(hg.material("Rain"))
    coll.objects.link(obj)
    return obj


def sky_dome(name, coll, radius=400.0):
    """Inside-out sphere for the storm clouds (unlit, additive over the black night sky)."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(hg.material("SkyClouds"))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        for loop in face.loops:
            co = loop.vert.co
            u = (math.atan2(co.y, co.x) / (2 * math.pi)) % 1.0
            v = 0.5 + math.asin(max(-1.0, min(1.0, co.z / radius))) / math.pi
            loop[uv_layer].uv = (u * 3.0, v)
    # Fix the seam: faces that wrap around get u + 3 on the low side.
    for face in bm.faces:
        us = [l[uv_layer].uv.x for l in face.loops]
        if max(us) - min(us) > 1.5:
            for l in face.loops:
                if l[uv_layer].uv.x < 1.5:
                    l[uv_layer].uv.x += 3.0
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def build():
    hg.reset_scene()
    coll = hg.collection("Kit_Outdoor")
    assets = [
        van("SM_Van", coll),
        van_side_door("SM_Van_SideDoor", coll),
        tree("SM_Tree_Oak_A", coll, seed=1),
        tree("SM_Tree_Oak_B", coll, seed=2, height=2.8, radius=0.55),
        tree("SM_Tree_Street", coll, seed=3, height=2.6, radius=0.28, canopy=1.25, twist=0.25, spread=0.7, rise=(0.6, 1.0)),
        tree("SM_Tree_Dead", coll, seed=4, height=2.2, radius=0.32, depth=4, leaves=False, twist=0.55),
        bush("SM_Bush_A", coll, seed=1),
        bush("SM_Bush_B", coll, seed=2, size=0.55, lumps=4),
        hedge("SM_Hedge_200", coll),
        grass_tuft("SM_Grass_Tuft_A", coll, seed=1),
        grass_tuft("SM_Grass_Tuft_B", coll, seed=2, blades=40, height=0.3),
        ufo("SM_UFO", coll),
        ufo_beam("SM_UFO_Beam", coll),
        ray_gun("SM_RayGun", coll),
        road("SM_Road_400", coll),
        curb("SM_Curb_400", coll),
        sidewalk("SM_Sidewalk_400", coll),
        mailbox("SM_Mailbox", coll),
        rain_curtains("SM_RainCurtains_1000", coll),
        sky_dome("SM_SkyDome", coll),
    ]
    for obj in assets:
        hg.export_fbx([obj], os.path.join(OUT, obj.name + ".fbx"))
    x = 0.0
    for obj in assets:
        obj.location.x = x + obj.dimensions.x / 2
        x += max(obj.dimensions.x, 0.5) + 1.0
    hg.save_blend(os.path.join(OUT, "Outdoor_Kit.blend"))
    print("exported %d outdoor assets to %s" % (len(assets), OUT))


build()
