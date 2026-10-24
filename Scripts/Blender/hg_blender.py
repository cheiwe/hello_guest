"""
Helpers for modelling Hello Guest assets in Blender from code.

Used by the asset scripts in Scripts/Blender/assets/. In Blender (or through the MCP) run an asset
script with:  exec(open(r"<project>/Scripts/Blender/assets/<name>.py", encoding="utf-8").read())

Conventions:
- 1 Blender unit = 1 m; FBX export scales to centimetres for Unreal.
- Forward is +X, up is +Z, the pivot of a prop is at the centre of its footprint on the floor;
  wall modules have their pivot at the bottom-left corner, running along +X, facing -Y.
- Materials are only named slots (M_<Name>) with a flat preview colour. Real surfaces are Unreal
  material instances of the same name, using tiling textures, so UVs are world-scale: 1 UV unit = 1 m.
"""

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

PROJECT = os.path.normpath(os.path.join(os.path.dirname(__file__) if "__file__" in globals() else r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender", "..", ".."))
MODELS_DIR = os.path.join(PROJECT, "SourceArt", "Models")

# Preview colours of the material slots (Unreal replaces them with textured material instances).
PALETTE = {
    "Wallpaper": (0.78, 0.66, 0.45),
    "WoodPanel": (0.36, 0.20, 0.10),
    "WoodDark": (0.22, 0.12, 0.06),
    "WoodFloor": (0.45, 0.25, 0.12),
    "WoodPainted": (0.30, 0.17, 0.10),
    "WoodWeathered": (0.48, 0.42, 0.36),
    "Trim": (0.85, 0.80, 0.70),
    "Plaster": (0.80, 0.74, 0.62),
    "Brass": (0.75, 0.55, 0.20),
    "MetalRust": (0.45, 0.26, 0.14),
    "MetalDark": (0.12, 0.12, 0.13),
    "Chain": (0.40, 0.30, 0.22),
    "PaintRed": (0.75, 0.16, 0.10),
    "PaintBlue": (0.35, 0.55, 0.70),
    "PaintYellow": (0.90, 0.72, 0.15),
    "PaintGreen": (0.30, 0.62, 0.25),
    "Web": (0.85, 0.85, 0.85),
    "Fabric": (0.30, 0.28, 0.20),
    "Rug": (0.42, 0.40, 0.30),
    "Glass": (0.70, 0.80, 0.80),
    "LampShade": (0.95, 0.80, 0.55),
    "Bakelite": (0.35, 0.33, 0.28),
    "Picture": (0.60, 0.55, 0.45),
    "Cardboard": (0.62, 0.46, 0.30),
    "Tape": (0.75, 0.65, 0.45),
    "WoodCrate": (0.55, 0.40, 0.25),
    "WoodWorn": (0.50, 0.34, 0.20),
    "MetalCan": (0.55, 0.55, 0.52),
    "MetalPainted": (0.42, 0.45, 0.42),
    "Paint": (0.85, 0.80, 0.70),
    "Label": (0.80, 0.72, 0.55),
    "Siding": (0.20, 0.36, 0.38),
    "Shingle": (0.28, 0.24, 0.22),
    "ShingleMoss": (0.35, 0.40, 0.25),
    "Moss": (0.30, 0.42, 0.18),
    "Brick": (0.55, 0.28, 0.20),
    "Concrete": (0.55, 0.55, 0.52),
    "ChainLink": (0.6, 0.6, 0.6),
    "Marble": (0.86, 0.84, 0.80),
    "MarbleDark": (0.70, 0.68, 0.64),
    "BookRed": (0.50, 0.12, 0.10),
    "BookGreen": (0.18, 0.32, 0.20),
    "BookBlue": (0.16, 0.22, 0.38),
    "BookBrown": (0.38, 0.22, 0.12),
    "BookOchre": (0.68, 0.50, 0.22),
    "Globe": (0.35, 0.55, 0.60),
    "Ink": (0.04, 0.03, 0.08),
    "Paper": (0.88, 0.84, 0.72),
    "Leather": (0.36, 0.20, 0.10),
    "GlassGreen": (0.10, 0.45, 0.20),
    "Gilt": (0.72, 0.55, 0.22),
    "GiltDark": (0.45, 0.32, 0.12),
    "Painting": (0.55, 0.45, 0.25),
    "WoodPaintedRed": (0.55, 0.22, 0.16),
    "WoodPaintedRedDark": (0.42, 0.16, 0.12),
    "Fabric_Light": (0.80, 0.78, 0.70),
    "Blanket": (0.55, 0.35, 0.30),
    "Screen": (0.25, 0.30, 0.28),
    "Porcelain": (0.90, 0.88, 0.82),
    "BulbGlass": (0.92, 0.92, 0.88),
    "CautionTape": (0.92, 0.78, 0.15),
    "BloodTrail": (0.35, 0.03, 0.02),
}


# --- Scene -----------------------------------------------------------------------------------------

def reset_scene():
    """Empty scene, metric units, no default objects or collections."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0


def collection(name):
    """Get or create a collection linked to the scene; each asset lives in its own collection."""
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def material(name):
    full = "M_" + name
    mat = bpy.data.materials.get(full)
    if mat is None:
        mat = bpy.data.materials.new(full)
        color = PALETTE.get(name, (0.6, 0.6, 0.6))
        mat.diffuse_color = (*color, 1.0)
        mat.use_nodes = True
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.7
    return mat


# --- Geometry --------------------------------------------------------------------------------------

def _link(obj, coll):
    coll.objects.link(obj)
    return obj


def box(name, size, location=(0, 0, 0), mat="WoodPanel", coll=None, bevel=0.0, rotation=(0, 0, 0)):
    """Box with its centre at location. size in metres. Optional bevel for the cartoon soft edges."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, affect="EDGES", profile=0.5)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material(mat))
    return _link(obj, coll or bpy.context.scene.collection)


def cylinder(name, radius, depth, location=(0, 0, 0), mat="MetalDark", coll=None, segments=16, rotation=(0, 0, 0), radius_top=None):
    """Cylinder (or cone with radius_top) along Z, centred at location."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius if radius_top is None else radius_top, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material(mat))
    return _link(obj, coll or bpy.context.scene.collection)


def rod(name, start, end, radius, mat="MetalDark", coll=None, segments=8):
    """Cylinder from one point to another (arms, pipes, legs)."""
    start, end = Vector(start), Vector(end)
    direction = end - start
    obj = cylinder(name, radius, direction.length, (start + end) / 2, mat, coll, segments)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    return obj


def sphere(name, radius, location=(0, 0, 0), mat="Brass", coll=None, segments=16, rings=8, scale=(1, 1, 1)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.scale = scale
    obj.data.materials.append(material(mat))
    return _link(obj, coll or bpy.context.scene.collection)


def torus(name, major, minor, location=(0, 0, 0), mat="Chain", coll=None, rotation=(0, 0, 0), scale=(1, 1, 1), segments=12, ring_segments=6):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts_ring = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        ring = []
        for j in range(ring_segments):
            b = 2 * math.pi * j / ring_segments
            r = major + minor * math.cos(b)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b))))
        verts_ring.append(ring)
    for i in range(segments):
        for j in range(ring_segments):
            a = verts_ring[i][j]
            b = verts_ring[(i + 1) % segments][j]
            c = verts_ring[(i + 1) % segments][(j + 1) % ring_segments]
            d = verts_ring[i][(j + 1) % ring_segments]
            bm.faces.new((a, b, c, d))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale
    obj.data.materials.append(material(mat))
    return _link(obj, coll or bpy.context.scene.collection)


def plane(name, size, location=(0, 0, 0), mat="Picture", coll=None, rotation=(0, 0, 0)):
    """Flat quad in the XZ plane facing -Y (for pictures, posters, webs). size = (width, height)."""
    mesh = bpy.data.meshes.new(name)
    w, h = size[0] / 2, size[1] / 2
    mesh.from_pydata([(-w, 0, -h), (w, 0, -h), (w, 0, h), (-w, 0, h)], [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.uv_layers[0].data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = uv
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material(mat))
    return _link(obj, coll or bpy.context.scene.collection)


def rotate_about_z(obj, angle):
    """
    Rotates an object around the world Z axis through the origin (location and orientation).
    Uses matrix_basis: matrix_world of a just-created object is not evaluated yet.
    """
    rot = Matrix.Rotation(angle, 4, "Z")
    obj.matrix_basis = rot @ obj.matrix_basis


def jitter(obj, amount=0.01, seed=0):
    """Small random vertex offsets: hand-made, slightly crooked look."""
    import random
    rnd = random.Random(seed)
    for v in obj.data.vertices:
        v.co += Vector((rnd.uniform(-amount, amount), rnd.uniform(-amount, amount), rnd.uniform(-amount, amount)))


def join(objects, name):
    """
    Joins objects into one mesh object (keeps material slots). Every asset is built around the world
    origin, so the origin of the result is put back there: that is the asset's pivot.
    """
    objects = [o for o in objects if o is not None]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = name
    result.data.name = name
    apply_transforms(result)
    set_origin(result, (0.0, 0.0, 0.0))
    return result


def world_uv(obj, scale=1.0):
    """Box-projected UVs in world units (1 UV = 1 m / scale) so tiling textures keep their size on any piece."""
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
    matrix = obj.matrix_world
    normal_matrix = matrix.to_3x3().inverted().transposed()
    for poly in mesh.polygons:
        n = (normal_matrix @ poly.normal).normalized()
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            co = matrix @ mesh.vertices[mesh.loops[li].vertex_index].co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            uv[li].uv = (u * scale, v * scale)


def mirror_y(obj):
    """
    Mirrors the mesh across Y. Unreal's Y axis is the mirror image of Blender's, so an asset whose
    Unreal-side layout matters (a door leaf running along +Y from its hinge) is built along +Y here and
    mirrored before export.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        v.co.y = -v.co.y
    bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def planar_uv(obj):
    """Top-down UVs stretched 0..1 over the object's footprint (rugs, signs: one picture per object)."""
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for loop in mesh.loops:
        co = mesh.vertices[loop.vertex_index].co
        uv[loop.index].uv = ((co.x - x0) / (x1 - x0), (co.y - y0) / (y1 - y0))


def apply_transforms(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def set_origin(obj, point):
    """Moves the object origin to a world point without moving the geometry."""
    offset = Vector(point) - obj.matrix_world.translation
    obj.data.transform(Matrix.Translation(-offset))
    obj.matrix_world.translation += offset


# --- Export ----------------------------------------------------------------------------------------

def export_fbx(objects, path):
    """Exports the objects as one FBX in centimetres, +X forward, Z up, with smoothing groups."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="X",
        axis_up="Z",
        mesh_smooth_type="FACE",
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,
    )
    return path


def save_blend(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
