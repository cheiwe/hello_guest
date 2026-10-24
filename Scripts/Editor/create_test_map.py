"""
Builds the grey-box test level /Game/Maps/L_Sandbox for Hello Guest.

Run in the Unreal Editor: Tools > Execute Python Script... > select this file
(or in the Output Log, Python mode: py "<project>/Scripts/Editor/create_test_map.py").
Running it again rebuilds the level from scratch.

The level contains the player's spawn, a simple neighbour house with the two restricted
entrance rooms, the Guest with patrol points, and test items: crowbar, boards, scissors,
spider web, the chained door with four locks, a fuse socket, a dark zone and throwable props.
"""

import unreal

MAP_PATH = "/Game/Maps/L_Sandbox"
WALL_HEIGHT = 300.0
WALL_THICKNESS = 20.0

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")


def hg_class(name):
    cls = unreal.load_class(None, "/Script/HelloGuest." + name)
    if cls is None:
        raise RuntimeError("Class %s not found - is the HelloGuest module compiled?" % name)
    return cls


def spawn(cls, location, yaw=0.0, label=None, folder=None):
    actor = actors.spawn_actor_from_class(cls, unreal.Vector(*location), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    if label:
        actor.set_actor_label(label)
    if folder:
        actor.set_folder_path(folder)
    return actor


def block(label, center, size, folder="Geometry"):
    """Static cube with the given size in centimetres."""
    actor = spawn(unreal.StaticMeshActor, center, label=label, folder=folder)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(CUBE)
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    return actor


def wall(label, x1, y1, x2, y2):
    """Axis-aligned wall from (x1, y1) to (x2, y2)."""
    center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0, WALL_HEIGHT / 2.0)
    if abs(x2 - x1) > abs(y2 - y1):
        size = (abs(x2 - x1), WALL_THICKNESS, WALL_HEIGHT)
    else:
        size = (WALL_THICKNESS, abs(y2 - y1), WALL_HEIGHT)
    return block(label, center, size)


def pickup(label, item, location):
    actor = spawn(hg_class("HGPickup"), location, label=label, folder="Items")
    actor.set_editor_property("item_id", item)
    return actor


def obstacle(label, required_item, flag, location, yaw=0.0, loudness=0.8):
    actor = spawn(hg_class("HGObstacle"), location, yaw=yaw, label=label, folder="Obstacles")
    actor.set_editor_property("required_item", required_item)
    actor.set_editor_property("flag_on_use", flag)
    actor.set_editor_property("noise_loudness", loudness)
    return actor


def patrol_point(label, location, min_phase=0, weight=1.0, restricted=False):
    actor = spawn(hg_class("HGPatrolPoint"), location, label=label, folder="Guest")
    actor.set_editor_property("min_phase", min_phase)
    actor.set_editor_property("weight", weight)
    actor.set_editor_property("restricted_room", restricted)
    return actor


def door_lock(lock_id, key_item, requires=(), blocked_by=None):
    lock = unreal.HGDoorLock()
    lock.set_editor_property("lock_id", lock_id)
    lock.set_editor_property("key_item", key_item)
    lock.set_editor_property("requires_locks", list(requires))
    if blocked_by is not None:
        lock.set_editor_property("blocked_by", blocked_by)
    return lock


def build():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        # Rebuild an existing (possibly empty or broken) level from scratch.
        if not level_editor.load_level(MAP_PATH):
            raise RuntimeError("Could not open " + MAP_PATH)
        old = [a for a in actors.get_all_level_actors() if not isinstance(a, (unreal.WorldSettings, unreal.Brush))]
        if old:
            actors.destroy_actors(old)
        unreal.log("Hello Guest: cleared %d actors from %s, rebuilding" % (len(old), MAP_PATH))
    elif not level_editor.new_level(MAP_PATH):
        raise RuntimeError("Could not create " + MAP_PATH)

    # --- Lighting and sky ---------------------------------------------------------
    sun = spawn(unreal.DirectionalLight, (0, 0, 1000), label="Sun", folder="Lighting")
    sun.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=-45.0, yaw=30.0), False)
    sun.get_editor_property("light_component").set_editor_property("atmosphere_sun_light", True)
    spawn(unreal.SkyAtmosphere, (0, 0, 0), label="SkyAtmosphere", folder="Lighting")
    sky = spawn(unreal.SkyLight, (0, 0, 500), label="SkyLight", folder="Lighting")
    sky.get_editor_property("light_component").set_editor_property("real_time_capture", True)
    spawn(unreal.ExponentialHeightFog, (0, 0, 0), label="Fog", folder="Lighting")

    # --- Ground and the player's house ---------------------------------------------
    block("Ground", (0, 0, -10), (6000, 5000, 20))
    block("PlayerHouse", (-2200, 0, 150), (600, 800, 300))
    start = spawn(unreal.PlayerStart, (-1700, 0, 100), label="HomeSpawn", folder="Player")
    start.set_editor_property("player_start_tag", "HomeSpawn")

    # --- Neighbour house: X 0..1600, Y -800..800, door in the front wall ---------------
    wall("Front_L", 0, -800, 0, -100)
    wall("Front_R", 0, 100, 0, 800)
    wall("Back", 1600, -800, 1600, 800)
    wall("Side_L", 0, -800, 1600, -800)
    wall("Side_R", 0, 800, 1600, 800)

    # Two rooms by the entrance (X 0..600) with doorways into the corridor.
    wall("RoomL_Corridor_A", 0, -100, 250, -100)
    wall("RoomL_Corridor_B", 350, -100, 600, -100)
    wall("RoomL_Back", 600, -800, 600, -100)
    wall("RoomR_Corridor_A", 0, 100, 250, 100)
    wall("RoomR_Corridor_B", 350, 100, 600, 100)
    wall("RoomR_Back", 600, 100, 600, 800)

    # Restricted area for the Guest's patrol (he only enters while chasing).
    restricted = hg_class("HGNavArea_GuestRestricted")
    for label, center in (("Restricted_RoomL", (300, -450, 150)), ("Restricted_RoomR", (300, 450, 150))):
        volume = spawn(unreal.NavModifierVolume, center, label=label, folder="Navigation")
        volume.set_actor_scale3d(unreal.Vector(3.0, 3.5, 1.5))
        volume.set_editor_property("area_class", restricted)

    nav = spawn(unreal.NavMeshBoundsVolume, (0, 0, 150), label="NavMeshBounds", folder="Navigation")
    nav.set_actor_scale3d(unreal.Vector(30.0, 25.0, 3.0))

    # --- Items and obstacles ------------------------------------------------------
    block("Table_RoomL", (300, -600, 40), (160, 80, 80), folder="Props")
    pickup("Crowbar", "Crowbar", (300, -600, 100))
    pickup("Scissors", "Scissors", (300, 600, 60))
    pickup("KeyRed", "KeyRed", (1300, -600, 60))
    pickup("KeyBlue", "KeyBlue", (1300, 600, 60))
    pickup("KeyYellow", "KeyYellow", (900, -650, 60))
    pickup("KeyGreen", "KeyGreen", (900, 650, 60))
    pickup("Fuse", "Fuse", (700, 0, 60))

    obstacle("StairsBoards", "Crowbar", "Obstacle.StairsBoards", (1000, 780, 0), yaw=90.0, loudness=1.0)
    web = obstacle("SpiderWeb", "Scissors", "Obstacle.SpiderWeb", (1570, 0, 0), loudness=0.1)
    web.set_actor_scale3d(unreal.Vector(0.3, 0.6, 0.6))

    door = spawn(hg_class("HGDoor"), (1580, -50, 0), label="ChainedDoor", folder="Doors")
    door.set_editor_property("locks", [
        door_lock("ChainRed", "KeyRed"),
        door_lock("ChainBlue", "KeyBlue"),
        door_lock("ChainYellow", "KeyYellow"),
        door_lock("Green", "KeyGreen", requires=("ChainRed", "ChainBlue", "ChainYellow"), blocked_by=web),
    ])

    socket = spawn(hg_class("HGItemSocket"), (1590, -600, 150), yaw=180.0, label="FuseBox", folder="Items")
    socket.set_editor_property("required_item", "Fuse")
    socket.set_editor_property("flag_on_use", "Puzzle.Fuse")

    dark = spawn(hg_class("HGDarkZone"), (500, 700, 100), label="DarkCorner", folder="Hiding")
    dark.set_actor_scale3d(unreal.Vector(0.7, 0.7, 0.7))

    for index, location in enumerate(((800, -300, 50), (850, 300, 50), (1200, 0, 50))):
        spawn(hg_class("HGThrowableProp"), location, label="Throwable_%d" % index, folder="Props")

    # --- Guest --------------------------------------------------------------------
    spawn(hg_class("HGGuestCharacter"), (1200, 0, 130), yaw=180.0, label="Guest", folder="Guest")
    patrol_point("Patrol_A", (800, -500, 0))
    patrol_point("Patrol_B", (800, 500, 0))
    patrol_point("Patrol_C", (1400, -500, 0))
    patrol_point("Patrol_D", (1400, 500, 0))
    patrol_point("Patrol_E", (1100, 0, 0))
    patrol_point("Peek_RoomL", (300, -400, 0), min_phase=1, weight=0.2, restricted=True)
    patrol_point("Peek_RoomR", (300, 400, 0), min_phase=1, weight=0.2, restricted=True)

    level_editor.save_current_level()
    unreal.log("Hello Guest: test level created at " + MAP_PATH)


build()
