"""
Builds the grey-box blockout of Act 1, /Game/Maps/L_Act1: the street, the player's house and the
neighbour house with all floors (basements, 1st and 2nd floor, attic, tower, steep roof) and the
back yard. Floor plan and heights: Docs/LEVEL_ACT1.md. Concepts: SourceArt/Concept/.

Run in the Unreal Editor: Tools > Execute Python Script... > select this file,
or from a terminal with the editor open: py Scripts/Tools/ue_run.py Scripts/Editor/create_act1_house.py
Running it again rebuilds the level from scratch.

Coordinates: 1 unit = 1 cm. The house front faces -X (the street), X grows towards the back yard,
Y < 0 is the left side when looking at the house from the street. Room and wall coordinates are wall
centre lines; walls and slabs are T thick.
"""

import math

import unreal

MAP_PATH = "/Game/Maps/L_Act1"
MATERIAL_DIR = "/Game/Maps/Act1"
T = 20.0

# Footprint of the neighbour house.
HOUSE_DEPTH = 1600.0
HALF_WIDTH = 500.0

# Heights: top of each floor above the ground, cm (see Docs/LEVEL_ACT1.md).
GROUND = 0.0
F1 = 40.0
F2 = 340.0
ATTIC = 620.0
EAVE = 680.0
RIDGE = EAVE + HALF_WIDTH  # 45 degree roof
LEDGE = 750.0
FUSE_BASEMENT = -260.0
CLOSED_BASEMENT = -320.0
FOUNDATION = -420.0

DOOR_WIDTH = 120.0   # narrower openings do not pass the Guest's navmesh (agent radius 42 cm)
DOOR_HEIGHT = 250.0  # the Guest is 230 cm tall
STEP_RISE = 20.0
JUMP_STEP = 62.0     # the player jumps ~74 cm high

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
BASE_MATERIAL = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial")

# Colour per kind of geometry, so the blockout reads at a glance.
COLORS = {
    "Ground": (0.18, 0.32, 0.12),
    "Street": (0.08, 0.08, 0.09),
    "Wall": (0.62, 0.62, 0.60),
    "Exterior": (0.55, 0.50, 0.40),
    "Floor": (0.36, 0.30, 0.24),
    "Stairs": (0.55, 0.40, 0.25),
    "Roof": (0.22, 0.18, 0.16),
    "Ledge": (0.85, 0.75, 0.30),
    "Prop": (0.45, 0.45, 0.70),
    "Boards": (0.50, 0.32, 0.15),
    "Fence": (0.30, 0.22, 0.14),
    "ChainLink": (0.55, 0.58, 0.60),
    "Hazard": (0.80, 0.15, 0.10),
    "PlayerHouse": (0.85, 0.80, 0.62),
}
materials = {}


# --- Helpers -------------------------------------------------------------------------------------

def hg_class(name):
    cls = unreal.load_class(None, "/Script/HelloGuest." + name)
    if cls is None:
        raise RuntimeError("Class %s not found - is the HelloGuest module compiled?" % name)
    return cls


def blockout_material(kind):
    if kind in materials:
        return materials[kind]
    name = "MI_Blockout_" + kind
    path = MATERIAL_DIR + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.load_asset(path)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, MATERIAL_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(material, BASE_MATERIAL)
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        material, "Color", unreal.LinearColor(*COLORS[kind], 1.0))
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    materials[kind] = material
    return material


def spawn(cls, location, yaw=0.0, label=None, folder=None):
    actor = actors.spawn_actor_from_class(cls, unreal.Vector(*location), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    if label:
        actor.set_actor_label(label)
    if folder:
        actor.set_folder_path(folder)
    return actor


def box(label, center, size, folder, kind, rotation=None):
    """Static cube with the given centre and size in centimetres."""
    actor = spawn(unreal.StaticMeshActor, center, label=label, folder=folder)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(CUBE)
    component.set_material(0, blockout_material(kind))
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    if rotation is not None:
        actor.set_actor_rotation(rotation, False)
    return actor


def block(label, x1, x2, y1, y2, z1, z2, folder="Geometry", kind="Wall"):
    """Box between two corners."""
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    z1, z2 = sorted((z1, z2))
    return box(label, ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), (x2 - x1, y2 - y1, z2 - z1), folder, kind)


def wall(label, axis, at, a1, a2, z1, z2, openings=(), folder="Geometry/Walls", kind="Wall", thickness=T, extend=False):
    """
    Wall along `axis` ("x" or "y") on the line `axis' = at`, from a1 to a2, z1..z2.
    openings: (b1, b2, bottom, top) - doors and windows; the wall is cut into pieces around them.
    extend: grow both ends by half the thickness to close outer corners. Inner walls end on wall
    centre lines instead, so their ends stay hidden inside the walls they meet.
    """
    a1, a2 = sorted((a1, a2))
    if extend:
        a1, a2 = a1 - thickness / 2, a2 + thickness / 2
    pieces = []
    cursor = a1
    for b1, b2, bottom, top in sorted(openings):
        if b1 > cursor:
            pieces.append((cursor, b1, z1, z2))
        if bottom > z1:
            pieces.append((b1, b2, z1, bottom))
        if top < z2:
            pieces.append((b1, b2, top, z2))
        cursor = b2
    if cursor < a2:
        pieces.append((cursor, a2, z1, z2))
    for index, (p1, p2, pz1, pz2) in enumerate(pieces):
        name = "%s_%d" % (label, index)
        if axis == "x":
            block(name, p1, p2, at - thickness / 2, at + thickness / 2, pz1, pz2, folder, kind)
        else:
            block(name, at - thickness / 2, at + thickness / 2, p1, p2, pz1, pz2, folder, kind)


def subtract_rect(rects, hole):
    hx1, hx2, hy1, hy2 = hole
    result = []
    for x1, x2, y1, y2 in rects:
        if hx1 >= x2 or hx2 <= x1 or hy1 >= y2 or hy2 <= y1:
            result.append((x1, x2, y1, y2))
            continue
        if x1 < hx1:
            result.append((x1, hx1, y1, y2))
        if hx2 < x2:
            result.append((hx2, x2, y1, y2))
        ix1, ix2 = max(x1, hx1), min(x2, hx2)
        if y1 < hy1:
            result.append((ix1, ix2, y1, hy1))
        if hy2 < y2:
            result.append((ix1, ix2, hy2, y2))
    return result


def slab(label, x1, x2, y1, y2, top, holes=(), folder="Geometry/Floors", kind="Floor", thickness=T):
    """Floor slab with rectangular holes (x1, x2, y1, y2) for stairs and hatches."""
    rects = [(x1, x2, y1, y2)]
    for hole in holes:
        rects = subtract_rect(rects, hole)
    for index, (rx1, rx2, ry1, ry2) in enumerate(rects):
        block("%s_%d" % (label, index), rx1, rx2, ry1, ry2, top - thickness, top, folder, kind)


def stairs(label, axis, start, end, c1, c2, z_start, z_end, folder="Geometry/Stairs"):
    """
    Solid stairs along `axis` from `start` (at height z_start) to `end` (at z_end), across c1..c2.
    Works both up and down: the first step is one rise away from z_start.
    """
    count = int(round(abs(z_end - z_start) / STEP_RISE))
    depth = (end - start) / count
    bottom = min(z_start, z_end) - T
    steps = []
    for index in range(count):
        a1 = start + depth * index
        a2 = a1 + depth
        top = z_start + (z_end - z_start) * (index + 1) / count
        name = "%s_%02d" % (label, index)
        if axis == "x":
            steps.append(block(name, a1, a2, c1, c2, bottom, top, folder, "Stairs"))
        else:
            steps.append(block(name, c1, c2, a1, a2, bottom, top, folder, "Stairs"))
    return steps


def roof_z(y):
    """Top of the roof surface above a point at distance |y| from the ridge."""
    return RIDGE - (RIDGE - EAVE) * abs(y) / HALF_WIDTH


def roof_piece(label, x1, x2, y1, y2):
    """Sloped roof slab between y1 and y2 (both on the same side of the ridge). The slope is unwalkable."""
    angle = math.atan2(RIDGE - EAVE, HALF_WIDTH)
    length = abs(y2 - y1) / math.cos(angle)
    yc = (y1 + y2) / 2
    zc = roof_z(yc) - (T / 2) / math.cos(angle)
    # Pick the roll sign that tilts the local Y axis up towards the ridge.
    rotation = None
    for roll in (math.degrees(angle), -math.degrees(angle)):
        candidate = unreal.Rotator(roll=roll, pitch=0.0, yaw=0.0)
        towards_ridge = candidate.get_right_vector() * (1.0 if yc < 0 else -1.0)
        if towards_ridge.z > 0:
            rotation = candidate
    actor = box(label, ((x1 + x2) / 2, yc, zc), (x2 - x1, length, T), "Geometry/Roof", "Roof", rotation)
    override = unreal.WalkableSlopeOverride()
    override.set_editor_property("walkable_slope_behavior", unreal.WalkableSlopeBehavior.WALKABLE_SLOPE_UNWALKABLE)
    actor.get_editor_property("static_mesh_component").set_walkable_slope_override(override)
    return actor


def gable(label, x):
    """Triangular gable wall above the eaves, stacked from boxes that stay under the roof."""
    layers = 10
    height = (RIDGE - EAVE) / layers
    for index in range(layers - 1):
        z1 = EAVE + height * index
        z2 = z1 + height
        half = HALF_WIDTH * (RIDGE - z2) / (RIDGE - EAVE)
        block("%s_%d" % (label, index), x - T / 2, x + T / 2, -half, half, z1, z2, "Geometry/Roof", "Exterior")


def span(start):
    """Door opening that starts at the hinge."""
    return (start, start + DOOR_WIDTH)


def door_on_x_wall(label, y, x1, floor, locks=(), folder="Doors"):
    """Door in a wall running along X (y = const). The hinge is at x1, the door is DOOR_WIDTH wide."""
    door = spawn(hg_class("HGDoor"), (x1, y, floor), yaw=-90.0, label=label, folder=folder)
    door.set_actor_scale3d(unreal.Vector(1.0, DOOR_WIDTH / 100.0, DOOR_HEIGHT / 210.0))
    if locks:
        door.set_editor_property("locks", list(locks))
    return door


def door_on_y_wall(label, x, y1, floor, locks=(), folder="Doors"):
    """Door in a wall running along Y (x = const). The hinge is at y1."""
    door = spawn(hg_class("HGDoor"), (x, y1, floor), yaw=0.0, label=label, folder=folder)
    door.set_actor_scale3d(unreal.Vector(1.0, DOOR_WIDTH / 100.0, DOOR_HEIGHT / 210.0))
    if locks:
        door.set_editor_property("locks", list(locks))
    return door


def door_lock(lock_id, key_item, requires=(), blocked_by=None):
    lock = unreal.HGDoorLock()
    lock.set_editor_property("lock_id", lock_id)
    lock.set_editor_property("key_item", key_item)
    lock.set_editor_property("requires_locks", list(requires))
    if blocked_by is not None:
        lock.set_editor_property("blocked_by", blocked_by)
    return lock


def obstacle(label, required_item, flag, center, yaw, width, height, loudness=0.8):
    """Obstacle filling an opening: `center` is the bottom middle of the opening, yaw 0 spans along Y."""
    actor = spawn(hg_class("HGObstacle"), center, yaw=yaw, label=label, folder="Obstacles")
    actor.set_actor_scale3d(unreal.Vector(1.0, width / 100.0, height / 200.0))
    actor.set_editor_property("required_item", required_item)
    actor.set_editor_property("flag_on_use", flag)
    actor.set_editor_property("noise_loudness", loudness)
    return actor


def pickup(label, item, location):
    actor = spawn(hg_class("HGPickup"), location, label=label, folder="Items")
    actor.set_editor_property("item_id", item)
    return actor


def item_socket(label, item, flag, location, yaw):
    """Socket facing local +X (yaw 0 faces +X)."""
    actor = spawn(hg_class("HGItemSocket"), location, yaw=yaw, label=label, folder="Items")
    actor.set_editor_property("required_item", item)
    actor.set_editor_property("flag_on_use", flag)
    return actor


def dark_zone(label, x1, x2, y1, y2, z1, z2):
    actor = spawn(hg_class("HGDarkZone"), ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), label=label, folder="Hiding")
    actor.set_actor_scale3d(unreal.Vector(abs(x2 - x1) / 300.0, abs(y2 - y1) / 300.0, abs(z2 - z1) / 300.0))
    return actor


def safe_zone(label, x1, x2, y1, y2, z1, z2):
    actor = spawn(hg_class("HGSafeZone"), ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), label=label, folder="Player")
    actor.set_actor_scale3d(unreal.Vector(abs(x2 - x1) / 300.0, abs(y2 - y1) / 300.0, abs(z2 - z1) / 300.0))
    return actor


def volume(cls, label, x1, x2, y1, y2, z1, z2, folder="Navigation"):
    """Brush volumes spawn as a 200 cm cube."""
    actor = spawn(cls, ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), label=label, folder=folder)
    actor.set_actor_scale3d(unreal.Vector(abs(x2 - x1) / 200.0, abs(y2 - y1) / 200.0, abs(z2 - z1) / 200.0))
    return actor


def patrol_point(label, location, min_phase=0, weight=1.0, restricted=False):
    actor = spawn(hg_class("HGPatrolPoint"), location, label=label, folder="Guest")
    actor.set_editor_property("min_phase", min_phase)
    actor.set_editor_property("weight", weight)
    actor.set_editor_property("restricted_room", restricted)
    return actor


def room_light(label, location, color=(1.0, 0.85, 0.65), intensity=1500.0, radius=900.0):
    light = spawn(unreal.PointLight, location, label=label, folder="Lighting/Rooms")
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    component.set_editor_property("intensity", intensity)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("light_color", unreal.Color(r=int(color[0] * 255), g=int(color[1] * 255), b=int(color[2] * 255), a=255))
    component.set_editor_property("cast_shadows", False)
    return light


# --- Level ---------------------------------------------------------------------------------------

def open_clean_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        if not level_editor.load_level(MAP_PATH):
            raise RuntimeError("Could not open " + MAP_PATH)
        old = [a for a in actors.get_all_level_actors() if not isinstance(a, (unreal.WorldSettings, unreal.Brush))]
        if old:
            actors.destroy_actors(old)
        unreal.log("Hello Guest: cleared %d actors from %s, rebuilding" % (len(old), MAP_PATH))
    elif not level_editor.new_level(MAP_PATH):
        raise RuntimeError("Could not create " + MAP_PATH)


def build_environment():
    sun = spawn(unreal.DirectionalLight, (0, 0, 2000), label="Sun", folder="Lighting")
    # Low evening sun from behind the player's house, as on the yard concepts.
    sun.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=-25.0, yaw=30.0), False)
    sun.get_editor_property("light_component").set_editor_property("atmosphere_sun_light", True)
    spawn(unreal.SkyAtmosphere, (0, 0, 0), label="SkyAtmosphere", folder="Lighting")
    sky = spawn(unreal.SkyLight, (0, 0, 1500), label="SkyLight", folder="Lighting")
    sky.get_editor_property("light_component").set_editor_property("real_time_capture", True)
    spawn(unreal.ExponentialHeightFog, (0, 0, 0), label="Fog", folder="Lighting")

    # Ground with a hole for the house footprint (the basements are below).
    for index, rect in enumerate(subtract_rect([(-3500, 4000, -2500, 2500)], (0, HOUSE_DEPTH, -HALF_WIDTH, HALF_WIDTH))):
        block("Ground_%d" % index, rect[0], rect[1], rect[2], rect[3], GROUND - 20, GROUND, "Exterior", "Ground")
    block("Street", -1500, -700, -2500, 2500, GROUND, GROUND + 2, "Exterior", "Street")
    block("Path", -700, -300, -100, 100, GROUND, GROUND + 2, "Exterior", "Street")

    # Player's house across the street (exterior only for now).
    block("PlayerHouse", -2700, -2000, -500, 500, GROUND, 650, "Exterior/PlayerHouse", "PlayerHouse")
    block("PlayerHouse_Roof", -2750, -1950, -550, 550, 650, 700, "Exterior/PlayerHouse", "Roof")
    start = spawn(unreal.PlayerStart, (-1800, 0, 100), label="HomeSpawn", folder="Player")
    start.set_editor_property("player_start_tag", "HomeSpawn")
    # The player's half of the street and his yard: the Guest gives up the chase at its edge.
    safe_zone("SafeZone_PlayerSide", -3500, -1100, -2500, 2500, GROUND - 100, 1000)


def build_back_yard():
    """Back yard behind a tall plank fence (Yard_01..03 concepts)."""
    folder = "Exterior/BackYard"
    fence = 250
    back, side, front = 3400, 1300, 1000
    wall("Fence_Back", "y", back, -side, side, GROUND, fence, folder=folder, kind="Fence", thickness=10, extend=True)
    wall("Fence_Left", "x", -side, front, back, GROUND, fence, folder=folder, kind="Fence", thickness=10)
    # Gate gap on the right side, the way in from the street.
    wall("Fence_Right", "x", side, front, back, GROUND, fence, folder=folder, kind="Fence", thickness=10,
         openings=[(1300, 1450, GROUND, fence)])
    wall("Fence_FrontLeft", "y", front, -side, -HALF_WIDTH, GROUND, fence, folder=folder, kind="Fence", thickness=10)
    wall("Fence_FrontRight", "y", front, HALF_WIDTH, side, GROUND, fence, folder=folder, kind="Fence", thickness=10)

    # Chain-link pen against the back wall around the broken pantry window.
    pen_x = 1850
    wall("ChainLink_Side", "x", -280, HOUSE_DEPTH, pen_x, GROUND, 300, folder=folder, kind="ChainLink", thickness=5)
    wall("ChainLink_Back", "y", pen_x, -HALF_WIDTH, -280, GROUND, 300, folder=folder, kind="ChainLink", thickness=5)
    wall("ChainLink_Outer", "x", -HALF_WIDTH, HOUSE_DEPTH, pen_x, GROUND, 300, folder=folder, kind="ChainLink", thickness=5)
    block("Crate_UnderPantryWindow", 1620, 1700, -430, -350, GROUND, 50, folder, "Prop")
    # Fire ladder next to the pen, up to the kids room window. Climbing is not implemented yet.
    block("FireLadder_Placeholder", 1612, 1630, -190, -150, GROUND, F2 + 60, folder, "Hazard")

    # Outhouse in the far corner under the big tree (antenna for the optional quest).
    wall("Outhouse_Back", "y", 3300, -1150, -1000, GROUND, 230, folder=folder, kind="Boards")
    wall("Outhouse_L", "x", -1150, 3150, 3300, GROUND, 230, folder=folder, kind="Boards")
    wall("Outhouse_R", "x", -1000, 3150, 3300, GROUND, 230, folder=folder, kind="Boards")
    block("Outhouse_Roof", 3130, 3320, -1170, -980, 230, 250, folder, "Boards")
    obstacle("OuthouseBoards", "Crowbar", "Obstacle.Outhouse", (3150, -1075, GROUND), 0.0, 150, 220)
    pickup("Antenna", "Antenna", (3240, -1075, 60))
    for label, x, y in (("Tree_Big", 2900, -700), ("Tree_Right", 3000, 900)):
        block(label + "_Trunk", x - 50, x + 50, y - 50, y + 50, GROUND, 700, folder, "Boards")
        block(label + "_Crown", x - 400, x + 400, y - 400, y + 400, 600, 1000, folder, "Ground")

    # Junk to hide behind and climb on: wood pile, barrels, crates, wheelbarrow.
    for label, rect in (("WoodPile", (2100, 2300, -1250, -1100, 80)), ("Barrel_A", (2000, 2070, -1050, -980, 100)),
                        ("Barrel_B", (2600, 2670, 500, 570, 100)), ("Crate_A", (2400, 2480, -200, -120, 60)),
                        ("Crate_B", (2250, 2330, 300, 380, 60)), ("Wheelbarrow", (2050, 2200, 100, 180, 70))):
        block(label, rect[0], rect[1], rect[2], rect[3], GROUND, rect[4], folder, "Prop")


def build_shell():
    """Foundations, floors, outer walls, porch."""
    w = HALF_WIDTH
    # Foundations under the parts without a basement: front rooms and the hallway.
    block("Foundation_Front", 0, 550, -w, w, FOUNDATION, F1 - T, "Geometry/Floors", "Floor")
    block("Foundation_Hall", 550, 1250, -75, 75, FOUNDATION, F1 - T, "Geometry/Floors", "Floor")
    # Fuse basement under the kitchen; closed basement under the back room and the stairwell.
    slab("Floor_FuseBasement", 550, 1250, -w, -75, FUSE_BASEMENT)
    slab("Floor_ClosedBasement_Back", 1250, HOUSE_DEPTH, -w, w, CLOSED_BASEMENT)
    slab("Floor_ClosedBasement_Under", 550, 1250, 75, w, CLOSED_BASEMENT)
    wall("Basement_FuseClosed", "y", 1250, -w, -75, FOUNDATION, F1 - T, folder="Geometry/Walls")

    slab("Floor_F1", 0, HOUSE_DEPTH, -w, w, F1, holes=[
        (1410, HOUSE_DEPTH, -175, 330),   # long stairs down to the closed basement
        (640, 1130, -w, -350),            # kitchen stairs down to the fuse basement
    ])
    slab("Floor_F2", 0, HOUSE_DEPTH, -w, w, F2, holes=[
        (600, 1120, 330, w),              # main stairs
    ])
    slab("Floor_Attic", 0, HOUSE_DEPTH, -w, w, ATTIC, holes=[
        (1490, 1590, 0, 280),             # attic hatch above the upstairs landing
    ])

    block("Porch", -300, 0, -250, 250, GROUND, F1, "Geometry/Exterior", "Floor")
    block("Porch_Step", -360, -300, -150, 150, GROUND, F1 / 2, "Geometry/Exterior", "Floor")

    f1_window = (F1 + 80, F1 + 200)
    f2_window = (F2 + 60, F2 + 180)
    wall("Ext_Front", "y", 0, -w, w, FOUNDATION, EAVE, kind="Exterior", folder="Geometry/Exterior", extend=True, openings=[
        (-60, 60, F1, F1 + DOOR_HEIGHT),             # front door
        (200, 400, f2_window[0], f2_window[1]),      # bedroom window
    ])
    wall("Ext_Left", "x", -w, 0, HOUSE_DEPTH, FOUNDATION, EAVE, kind="Exterior", folder="Geometry/Exterior", extend=True, openings=[
        (850, 1000, f1_window[0], f1_window[1]),     # kitchen window
        span(1120) + (F1, F1 + DOOR_HEIGHT),          # kitchen side door into the back yard
    ])
    block("SideDoor_Step", 1120, 1240, -w - 60, -w - 10, GROUND, F1 / 2, "Geometry/Exterior", "Floor")
    wall("Ext_Right", "x", w, 0, HOUSE_DEPTH, FOUNDATION, EAVE, kind="Exterior", folder="Geometry/Exterior", extend=True, openings=[
        (610, 690, GROUND + 100, GROUND + 220),      # stairwell window, sill 1.0 m above the yard
    ])
    wall("Ext_Back", "y", HOUSE_DEPTH, -w, w, FOUNDATION, EAVE, kind="Exterior", folder="Geometry/Exterior", extend=True, openings=[
        (-430, -330, GROUND + 100, GROUND + 200),    # broken pantry window inside the chain-link pen
        (-220, -120, GROUND + 400, GROUND + 520),    # kids room window above the fire ladder, sill 4.0 m
        (200, 350, f2_window[0], f2_window[1]),      # upstairs landing window
    ])

    # Boarded windows on the front.
    for label, y, z in (("Boards_Storage", -300, f1_window), ("Boards_Study", 300, f1_window), ("Boards_BulbRoom", -300, f2_window)):
        block(label, -25, -12, y - 110, y + 110, z[0], z[1], "Geometry/Exterior", "Boards")


def build_first_floor():
    h1, h2 = F1, F2 - T
    door = (F1, F1 + DOOR_HEIGHT)
    window = (F1 + 80, F1 + 200)
    # Narrow hallway (1.5 m) that widens into a vestibule at the chained door (Hallway concepts).
    wall("F1_HallLeft", "x", -75, 0, 1000, h1, h2, openings=[span(225) + door, span(650) + door])
    wall("F1_HallRight", "x", 75, 0, 1000, h1, h2, openings=[span(225) + door, (600, 800, F1, F1 + DOOR_HEIGHT)])
    wall("F1_VestibuleLeft_A", "y", 1000, -175, -75, h1, h2)
    wall("F1_VestibuleRight_A", "y", 1000, 75, 175, h1, h2)
    wall("F1_VestibuleLeft_B", "x", -175, 1000, 1250, h1, h2)
    wall("F1_VestibuleRight_B", "x", 175, 1000, 1250, h1, h2)
    wall("F1_Storage_Kitchen", "y", 550, -HALF_WIDTH, -75, h1, h2)
    wall("F1_Study_Stairwell", "y", 550, 75, HALF_WIDTH, h1, h2)
    # Back wall of the hallway: chained door with a narrow window on each side, pantry door.
    wall("F1_BackRoomWall", "y", 1250, -HALF_WIDTH, HALF_WIDTH, h1, h2, openings=[
        span(-400) + door, (-155, -95) + window, span(-60) + door, (95, 155) + window])
    wall("F1_Pantry_StairRoom", "x", -175, 1250, HOUSE_DEPTH, h1, h2)
    # Railings around the openings down.
    wall("F1_LongStairsRail", "y", 1415, -175, 330, h1, h1 + 100)
    wall("F1_KitchenRail_A", "x", -350, 640, 1120, h1, h1 + 100)
    wall("F1_KitchenRail_B", "y", 640, -HALF_WIDTH, -350, h1, h1 + 100)

    stairs("Stairs_F1_F2", "x", 640, 1120, 330, 490, F1, F2)
    # Entered from the back of the kitchen, so the bottom opens into the basement and not into a wall.
    stairs("Stairs_Kitchen_Basement", "x", 1130, 650, -490, -360, F1, FUSE_BASEMENT)
    long_stairs = stairs("Stairs_ClosedBasement", "y", 330, -170, 1420, 1590, F1, CLOSED_BASEMENT)
    long_stairs[7].set_actor_label("Stairs_ClosedBasement_07_FalseStep")
    long_stairs[7].get_editor_property("static_mesh_component").set_material(0, blockout_material("Hazard"))

    door_on_y_wall("Door_Front", 0, -60, F1)
    door_on_x_wall("Door_Storage", -75, 225, F1)
    door_on_x_wall("Door_Study", 75, 225, F1)
    door_on_x_wall("Door_Kitchen", -75, 650, F1)
    door_on_y_wall("Door_Pantry", 1250, -400, F1)
    # The Guest's own way between the house and the yard, so he does not walk round by the front door.
    door_on_x_wall("Door_KitchenSide", -HALF_WIDTH, 1120, F1)
    # Wide arch to the stairs, boarded up.
    obstacle("StairsBoards", "Crowbar", "Obstacle.StairsBoards", (700, 75, F1), 90.0, 200, DOOR_HEIGHT, 1.0)

    web = obstacle("SpiderWeb", "Scissors", "Obstacle.SpiderWeb", (1235, 0, F1 + 60), 0.0, 60, 80, 0.1)
    door_on_y_wall("ChainedDoor", 1250, -60, F1, locks=[
        door_lock("ChainRed", "KeyRed"),
        door_lock("ChainBlue", "KeyBlue"),
        door_lock("ChainYellow", "KeyYellow"),
        door_lock("Green", "KeyGreen", requires=("ChainRed", "ChainBlue", "ChainYellow"), blocked_by=web),
    ])

    # Hallway: coat rack and the telephone table by the chained door.
    block("Hall_CoatRack", 1020, 1060, -160, -120, F1, F1 + 180, "Props/F1", "Prop")
    block("Hall_PhoneTable", 1170, 1235, 100, 165, F1, F1 + 80, "Props/F1", "Prop")

    # Storage (left, restricted for the Guest): table with the crowbar.
    block("Storage_Table", 150, 350, -480, -400, F1, F1 + 80, "Props/F1", "Prop")
    pickup("Crowbar", "Crowbar", (250, -440, F1 + 100))
    block("Storage_Cabinet", 440, 530, -480, -300, F1, F1 + 200, "Props/F1", "Prop")

    # Study (right, restricted): desk and pedestal for the painting puzzle (puzzle logic is not implemented yet).
    block("Study_Desk", 250, 400, 380, 480, F1, F1 + 80, "Props/F1", "Prop")
    block("Study_Pedestal", 440, 500, 400, 460, F1, F1 + 110, "Props/F1", "Prop")
    block("Study_Bookshelf", 20, 60, 120, 480, F1, F1 + 220, "Props/F1", "Prop")
    pickup("KeyRed_Placeholder", "KeyRed", (325, 430, F1 + 100))

    # Kitchen / dining room: table, counter with the small key to the upstairs door.
    block("Kitchen_Counter", 560, 640, -340, -190, F1, F1 + 90, "Props/F1", "Prop")
    # Against the hallway wall: the stairs down leave only a narrow band of the kitchen free.
    block("Dining_Table", 840, 980, -170, -95, F1, F1 + 75, "Props/F1", "Prop")
    pickup("UpstairsKey", "UpstairsKey", (600, -265, F1 + 110))

    # Pantry behind the kitchen: the broken window to the chain-link pen.
    block("Pantry_Shelf", 1270, 1310, -480, -200, F1, F1 + 200, "Props/F1", "Prop")

    # Basements.
    block("FuseBasement_Cabinet", 1170, 1230, -340, -260, FUSE_BASEMENT, FUSE_BASEMENT + 200, "Props/Basement", "Prop")
    block("FuseBasement_WaterHeater", 580, 680, -200, -100, FUSE_BASEMENT, FUSE_BASEMENT + 180, "Props/Basement", "Prop")
    # Fuse box: the breaker lever is not implemented yet, the socket sets the breaker flag directly.
    item_socket("FuseBox", "Fuse", "Puzzle.Breaker", (1235, -200, FUSE_BASEMENT + 150), 180.0)

    block("ClosedBasement_Console", 570, 650, 150, 450, CLOSED_BASEMENT, CLOSED_BASEMENT + 90, "Props/Basement", "Prop")
    block("ClosedBasement_Monitors", 560, 600, 150, 450, CLOSED_BASEMENT + 90, CLOSED_BASEMENT + 200, "Props/Basement", "Hazard")
    block("ClosedBasement_Tapes", 900, 1000, 400, 480, CLOSED_BASEMENT, CLOSED_BASEMENT + 140, "Props/Basement", "Prop")


def build_second_floor():
    h1, h2 = F2, ATTIC - T
    door = (F2, F2 + DOOR_HEIGHT)
    wall("F2_HallLeft", "x", -75, 0, 1250, h1, h2, openings=[span(225) + door, span(650) + door])
    wall("F2_HallRight", "x", 75, 0, 1250, h1, h2, openings=[span(225) + door, span(880) + door])
    wall("F2_Bulb_Apple", "y", 550, -HALF_WIDTH, -75, h1, h2)
    wall("F2_Bedroom_Safe", "y", 550, 75, HALF_WIDTH, h1, h2)
    wall("F2_StairShaft", "x", 310, 550, 1250, h1, h2)
    wall("F2_Apple_Kids", "y", 1250, -HALF_WIDTH, -75, h1, h2, openings=[span(-350) + door])
    wall("F2_Safe_Landing", "y", 1250, 75, 310, h1, h2)
    wall("F2_Shaft_Landing", "y", 1250, 310, HALF_WIDTH, h1, h2, openings=[span(350) + door])
    wall("F2_Kids_Landing", "x", -75, 1250, HOUSE_DEPTH, h1, h2)

    door_on_y_wall("Door_Upstairs", 1250, 350, F2, locks=[door_lock("Upstairs", "UpstairsKey")])
    door_on_x_wall("Door_BulbRoom", -75, 225, F2)
    door_on_x_wall("Door_AppleRoom", -75, 650, F2)
    door_on_x_wall("Door_Bedroom", 75, 225, F2)
    door_on_x_wall("Door_SafeRoom", 75, 880, F2)
    obstacle("PoliceTape", "Scissors", "Obstacle.PoliceTape", (1250, 0, F2), 0.0, 150, 120, 0.1)
    obstacle("KidsRoomBoards", "Crowbar", "Obstacle.KidsRoomBoards", (1250, -350 + DOOR_WIDTH / 2, F2), 0.0, DOOR_WIDTH, DOOR_HEIGHT, 1.0)

    # Landing behind the upstairs door: scissors.
    block("Landing_Dresser", 1450, 1580, 380, 480, F2, F2 + 90, "Props/F2", "Prop")
    pickup("Scissors", "Scissors", (1515, 430, F2 + 110))
    # Placeholder for the attic ladder that should come down after the breaker; for now always there.
    # Along the back wall, so it does not cut the landing in two.
    stairs("AtticLadder_Placeholder", "y", 0, 280, 1490, 1590, F2, ATTIC)

    # Hallway: the painting with the desk arrangement and the blood trail.
    block("Hall_Painting", 500, 700, 60, 67, F2 + 120, F2 + 220, "Props/F2", "Hazard")
    block("Hall_BloodTrail", 150, 1230, 10, 50, F2, F2 + 1, "Props/F2", "Hazard")

    # Bulb room (dark): four sockets on two opposite walls, bulbs scattered around.
    for index, (x, y, yaw) in enumerate(((12, -420, 0.0), (12, -150, 0.0), (538, -420, 180.0), (538, -150, 180.0))):
        item_socket("BulbSocket_%d" % (index + 1), "Bulb", "Puzzle.Bulb%d" % (index + 1), (x, y, F2 + 200), yaw)
    block("BulbRoom_Boxes_A", 80, 220, -480, -380, F2, F2 + 120, "Props/F2", "Prop")
    block("BulbRoom_Boxes_B", 380, 500, -200, -100, F2, F2 + 150, "Props/F2", "Prop")
    block("BulbRoom_Table", 200, 350, -330, -250, F2, F2 + 75, "Props/F2", "Prop")
    block("BulbRoom_Shelf", 490, 530, -400, -230, F2, F2 + 200, "Props/F2", "Prop")
    block("BulbRoom_RedNumbers", 10, 12, -330, -230, F2 + 120, F2 + 200, "Props/F2", "Hazard")
    for index, location in enumerate(((150, -430, F2 + 140), (510, -315, F2 + 220), (275, -290, F2 + 10), (440, -150, F2 + 170))):
        pickup("Bulb_%d" % (index + 1), "Bulb", location)

    # Safe room: the safe puzzle is not implemented yet, the blue key lies on top of the safe.
    block("Safe", 1130, 1230, 200, 290, F2, F2 + 120, "Props/F2", "Prop")
    pickup("KeyBlue_Placeholder", "KeyBlue", (1180, 245, F2 + 140))

    # Golden apple room: paintings on the back wall, the boarded door to the right of them.
    for index, y in enumerate((-460, -170)):
        block("Apple_Painting_%d" % index, 1236, 1240, y - 40, y + 40, F2 + 120, F2 + 200, "Props/F2", "Ledge")
    block("Apple_Wardrobe", 600, 660, -480, -280, F2, F2 + 210, "Props/F2", "Prop")

    # Bedroom (front right): bed and wardrobe to hide behind.
    block("Bedroom_Bed", 300, 520, 300, 480, F2, F2 + 50, "Props/F2", "Prop")
    block("Bedroom_Wardrobe", 20, 80, 100, 250, F2, F2 + 210, "Props/F2", "Prop")

    # Kids room behind the boards: fuse, marbles box, window to the fire ladder.
    block("Kids_Bed", 1350, 1580, -480, -380, F2, F2 + 50, "Props/F2", "Prop")
    block("Kids_ToyBox", 1300, 1380, -160, -90, F2, F2 + 60, "Props/F2", "Prop")
    pickup("Fuse", "Fuse", (1340, -125, F2 + 80))


def build_attic_and_roof():
    w = HALF_WIDTH
    # Low knee walls are part of the outer walls (up to EAVE).
    block("Radio_Station", 1480, 1590, -330, -30, ATTIC, ATTIC + 180, "Props/Attic", "Prop")
    block("Radio_RedBox", 1520, 1590, -420, -350, ATTIC, ATTIC + 60, "Props/Attic", "Hazard")
    pickup("KeyYellow_Placeholder", "KeyYellow", (1460, -180, ATTIC + 30))
    # Weak floor on the way to the radio (the trap itself is not implemented yet).
    block("Attic_WeakFloor", 1200, 1350, -80, 80, ATTIC, ATTIC + 1, "Props/Attic", "Hazard")
    # Built-in wardrobe nailed shut, the green key inside.
    wall("Wardrobe_Back", "x", 300, 500, 700, ATTIC, ATTIC + 200, folder="Props/Attic", kind="Prop")
    wall("Wardrobe_L", "y", 500, 100, 300, ATTIC, ATTIC + 200, folder="Props/Attic", kind="Prop")
    wall("Wardrobe_R", "y", 700, 100, 300, ATTIC, ATTIC + 200, folder="Props/Attic", kind="Prop")
    block("Wardrobe_Top", 490, 710, 90, 310, ATTIC + 200, ATTIC + 210, "Props/Attic", "Prop")
    obstacle("WardrobeBoards", "Crowbar", "Obstacle.WardrobeBoards", (600, 100, ATTIC), 90.0, 200, 200, 1.0)
    pickup("KeyGreen", "KeyGreen", (600, 210, ATTIC + 30))

    # Tower at the left eave (X 300..600, Y -500..-250), sticking out of the roof.
    tower_top = 1150.0
    tx1, tx2, ty = 300, 600, -250
    wall("Tower_Front", "y", tx1, -w, ty, ATTIC, tower_top, folder="Geometry/Tower", kind="Exterior")
    wall("Tower_Back", "y", tx2, -w, ty, ATTIC, tower_top, folder="Geometry/Tower", kind="Exterior")
    wall("Tower_Inner", "x", ty, tx1, tx2, ATTIC, tower_top, folder="Geometry/Tower", kind="Exterior",
         openings=[(400, 500, ATTIC, ATTIC + 200)])
    # Hole in the outer wall leading to the ledge.
    wall("Tower_Outer", "x", -w, tx1, tx2, EAVE, tower_top, folder="Geometry/Tower", kind="Exterior",
         openings=[(400, 500, LEDGE, LEDGE + 150)])
    block("Tower_Roof", tx1 - 20, tx2 + 20, -w - 20, ty + 20, tower_top, tower_top + 20, "Geometry/Tower", "Roof")
    block("Tower_Cap", tx1 + 80, tx2 - 80, -w + 80, ty - 80, tower_top + 20, tower_top + 180, "Geometry/Tower", "Roof")
    block("Tower_Platform", tx1 + 10, tx2 - 10, -w + 10, -400, ATTIC, LEDGE, "Geometry/Tower", "Prop")
    block("Tower_Crate", tx1 + 10, tx1 + 110, -400, -320, ATTIC, ATTIC + 65, "Geometry/Tower", "Prop")

    # Steep roof (45 degrees, unwalkable), cut around the tower. No overhang: it would hit the
    # player's head on the ledge.
    roof_piece("Roof_L_Front", -10, tx1, -w, 0)
    roof_piece("Roof_L_Tower", tx1, tx2, ty, 0)
    roof_piece("Roof_L_Back", tx2, HOUSE_DEPTH + 10, -w, 0)
    roof_piece("Roof_R", -10, HOUSE_DEPTH + 10, 0, w)
    gable("Gable_Front", 0)
    gable("Gable_Back", HOUSE_DEPTH)
    block("Roof_RidgeCap", -10, HOUSE_DEPTH + 10, -40, 40, RIDGE - T, RIDGE, "Geometry/Roof", "Ledge")

    # Cornice ledge: from the tower hole along the left eave, then round the corner onto the front gable.
    block("Ledge_Side", -80, tx2, -w - 60, -w - 10, LEDGE - T, LEDGE, "Geometry/Roof", "Ledge")
    block("Ledge_Front", -80, -20, -w - 60, -380, LEDGE - T, LEDGE, "Geometry/Roof", "Ledge")
    # Stone brackets up the front gable: one jump each, staggered so the next one does not hit the head.
    for index in range(1, 7):
        y = -420 + 70 * index
        z = LEDGE + JUMP_STEP * index
        block("Ledge_Bracket_%d" % index, -80, -20, y - 30, y + 30, z - T, z, "Geometry/Roof", "Ledge")

    # Spire at the front of the ridge, with the antenna mount (optional quest).
    block("Spire", 140, 160, -10, 10, RIDGE, RIDGE + 300, "Geometry/Roof", "Hazard")
    item_socket("AntennaMount", "Antenna", "Quest.Antenna", (150, -25, RIDGE + 80), -90.0)


def build_gameplay():
    w = HALF_WIDTH
    # Rooms the Guest does not patrol: storage and study by the entrance.
    restricted = hg_class("HGNavArea_GuestRestricted")
    for label, rect in (("Restricted_Storage", (0, 550, -w, -75)), ("Restricted_Study", (0, 550, 75, w))):
        nav_volume = volume(unreal.NavModifierVolume, label, rect[0], rect[1], rect[2], rect[3], F1 - 20, F2 - T)
        nav_volume.set_editor_property("area_class", restricted)
    volume(unreal.NavMeshBoundsVolume, "NavMeshBounds", -3500, 4000, -2500, 2500, FOUNDATION - 50, RIDGE + 100)

    dark_zone("Dark_StorageCorner", 400, 550, -w, -250, F1, F1 + 200)
    dark_zone("Dark_UnderStairs", 1050, 1250, 180, 320, F1, F1 + 200)
    dark_zone("Dark_BulbRoom", 0, 550, -w, -75, F2, F2 + 250)
    dark_zone("Dark_Bedroom", 0, 200, 75, 300, F2, F2 + 200)
    dark_zone("Dark_AtticCorner", 0, 300, 100, 400, ATTIC, ATTIC + 150)
    dark_zone("Dark_ClosedBasement", 550, 1250, 75, w, CLOSED_BASEMENT, CLOSED_BASEMENT + 300)

    throwables = ((150, 0, F1 + 30), (910, -130, F1 + 100), (900, 300, F1 + 30),
                  (400, 30, F2 + 30), (1450, 300, F2 + 30), (900, -300, F2 + 30), (2300, -150, 90))
    for index, location in enumerate(throwables):
        spawn(hg_class("HGThrowableProp"), location, label="Throwable_%d" % index, folder="Props/Throwables")

    # At the start the Guest keeps to the back of the house, the kitchen, the basement and the yard,
    # away from the entrance where the player comes in. The stairwell opens once the boards are gone.
    spawn(hg_class("HGGuestCharacter"), (1120, -40, F1 + 125), yaw=180.0, label="Guest", folder="Guest")
    patrol_point("Patrol_F1_Vestibule", (1120, 0, F1))
    patrol_point("Patrol_F1_Kitchen", (850, -250, F1))
    patrol_point("Patrol_F1_Pantry", (1420, -330, F1), weight=0.7)
    patrol_point("Patrol_FuseBasement", (900, -250, FUSE_BASEMENT), weight=0.5)
    patrol_point("Patrol_BackYard", (2400, 0, GROUND), weight=0.7)
    patrol_point("Patrol_BackYard_Outhouse", (2900, -1000, GROUND), weight=0.4)
    patrol_point("Patrol_F1_Stairwell", (900, 250, F1), min_phase=1)
    patrol_point("Patrol_F1_Hall", (700, 0, F1), min_phase=1, weight=0.5)
    patrol_point("Peek_Storage", (300, -250, F1), min_phase=1, weight=0.2, restricted=True)
    patrol_point("Peek_Study", (300, 250, F1), min_phase=1, weight=0.2, restricted=True)
    patrol_point("Patrol_F2_Landing", (1450, 250, F2), min_phase=1)
    patrol_point("Patrol_F2_Hall", (400, 0, F2), min_phase=2)
    patrol_point("Patrol_F2_SafeRoom", (900, 200, F2), min_phase=2, weight=0.5)
    patrol_point("Patrol_F2_AppleRoom", (900, -300, F2), min_phase=2, weight=0.5)

    room_light("Light_Hall", (500, 0, F2 - 60))
    room_light("Light_Vestibule", (1120, 0, F2 - 60), intensity=900.0)
    room_light("Light_Kitchen", (850, -300, F2 - 60))
    room_light("Light_Stairwell", (900, 300, F2 + 100))
    room_light("Light_Storage", (300, -300, F2 - 60), intensity=600.0)
    room_light("Light_Study", (300, 300, F2 - 60))
    room_light("Light_StairRoom", (1330, 200, F2 - 60), intensity=500.0)
    room_light("Light_F2_Hall", (500, 0, ATTIC - 60), intensity=900.0)
    room_light("Light_F2_Landing", (1420, 250, ATTIC - 60))
    room_light("Light_SafeRoom", (900, 200, ATTIC - 60), intensity=500.0)
    room_light("Light_AppleRoom", (900, -300, ATTIC - 60))
    room_light("Light_KidsRoom", (1420, -300, ATTIC - 60))
    room_light("Light_Bedroom", (300, 300, ATTIC - 60), intensity=600.0)
    room_light("Light_Attic", (1000, 0, RIDGE - 150), intensity=700.0, radius=1200.0)
    room_light("Light_FuseBasement", (900, -300, -60), color=(0.55, 0.75, 1.0), intensity=800.0)
    room_light("Light_ClosedBasement", (900, 300, -60), color=(1.0, 0.1, 0.05), intensity=600.0)


def build():
    open_clean_level()
    build_environment()
    build_back_yard()
    build_shell()
    build_first_floor()
    build_second_floor()
    build_attic_and_roof()
    build_gameplay()
    level_editor.save_current_level()
    unreal.log("Hello Guest: Act 1 blockout created at " + MAP_PATH)


build()
