"""
Review level for the hallway art kit: /Game/Maps/Preview/L_Art_HallwayPreview, a short corridor like the
Hallway_01 concept built from /Game/Art/Hallway assets, with a PlayerStart to walk around in.

    py Scripts/Tools/ue_run.py Scripts/Editor/create_art_preview_hallway.py

Unreal-side conventions of the kit (see Scripts/Blender/hg_blender.py):
- walls: pivot at the bottom-left end, run along +X (yaw 90: along +Y), centred on their thickness;
- door leaf and chains: pivot at the hinge, leaf along +Y, chains on the -X side;
- wall-mounted props (sconce, photo frame): back at local Y=0, facing +Y;
- floor and ceiling tiles: 1 x 1 m, pivot in the centre.
"""

import unreal

MAP_PATH = "/Game/Maps/Preview/L_Art_HallwayPreview"
KIT = "/Game/Art/Hallway/"
MATERIALS = "/Game/Art/Materials/"

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def open_clean_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        level_editor.load_level(MAP_PATH)
        old = [a for a in actors.get_all_level_actors() if not isinstance(a, (unreal.WorldSettings, unreal.Brush))]
        actors.destroy_actors(old)
    else:
        level_editor.new_level(MAP_PATH)


def mesh(name, location, yaw=0.0, folder="Hallway", label=None, material=None, slot=None):
    actor = actors.spawn_actor_from_object(unreal.load_asset(KIT + name), unreal.Vector(*location), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    actor.set_folder_path(folder)
    if label:
        actor.set_actor_label(label)
    if material:
        component = actor.get_editor_property("static_mesh_component")
        index = 0 if slot is None else component.get_material_index(slot)
        component.set_material(index, unreal.load_asset(MATERIALS + material))
    return actor


def point_light(label, location, intensity, radius, color=(255, 200, 140), shadows=True):
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*location))
    light.set_actor_label(label)
    light.set_folder_path("Lighting")
    c = light.get_editor_property("point_light_component")
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", intensity)
    c.set_editor_property("attenuation_radius", radius)
    c.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    c.set_editor_property("cast_shadows", shadows)
    return light


def build():
    open_clean_level()

    # Floor and ceiling: X 0..500, Y -200..200.
    for x in range(5):
        for y in range(4):
            cx, cy = x * 100 + 50, y * 100 - 150
            mesh("SM_Floor_Planks_100", (cx, cy, 0), folder="Hallway/Floor")
            mesh("SM_Ceiling_100", (cx, cy, 280), folder="Hallway/Ceiling")

    # Side walls (Y = -180 and +180), doorways into side rooms.
    for name, x in (("SM_Wall_Door_160", 0), ("SM_Wall_200", 160), ("SM_Wall_Door_160", 360)):
        mesh(name, (x, -180, 0), folder="Hallway/Walls")
    for name, x in (("SM_Wall_200", 0), ("SM_Wall_Door_160", 200), ("SM_Wall_Door_160", 360)):
        mesh(name, (x, 180, 0), folder="Hallway/Walls")
    # End wall at X = 520: narrow window, chained door, narrow window.
    for name, y in (("SM_Wall_WindowNarrow_100", -180), ("SM_Wall_Door_160", -80), ("SM_Wall_WindowNarrow_100", 80)):
        mesh(name, (520, y, 0), yaw=90, folder="Hallway/Walls")

    # Chained door: hinge at the opening's -Y edge, leaf along +Y. Padlocks hang on the chains.
    hinge = unreal.Vector(520, -60, 0)
    mesh("SM_Door_Panel", (hinge.x, hinge.y, 0), folder="Hallway/ChainedDoor", label="ChainedDoor_Leaf")
    mesh("SM_ChainedDoor_Chains", (hinge.x, hinge.y, 0), folder="Hallway/ChainedDoor")
    for y, z, material in ((35, 178, "MI_PaintRed"), (95, 169, "MI_PaintYellow"), (55, 88, "MI_PaintBlue")):
        mesh("SM_Padlock", (hinge.x - 8, hinge.y + y, z), folder="Hallway/ChainedDoor", material=material)
    mesh("SM_Padlock_Big", (hinge.x - 9, hinge.y + 74, 165), folder="Hallway/ChainedDoor")
    mesh("SM_SpiderWeb", (hinge.x - 11, hinge.y + 74, 145), folder="Hallway/ChainedDoor")

    # Furniture and decoration (Hallway_01, Hallway_02).
    mesh("SM_CoatRack", (455, -135, 0), folder="Hallway/Props")
    mesh("SM_PhoneTable", (475, 145, 0), yaw=90, folder="Hallway/Props")
    mesh("SM_RotaryPhone", (475, 140, 80), yaw=90, folder="Hallway/Props")
    mesh("SM_WallSconce", (490, -166, 185), yaw=0, folder="Hallway/Props")
    mesh("SM_WallSconce", (490, 166, 185), yaw=180, folder="Hallway/Props")
    mesh("SM_PhotoFrame", (120, -166, 160), yaw=0, folder="Hallway/Props")
    mesh("SM_PhotoFrame", (280, 166, 155), yaw=180, folder="Hallway/Props", material="MI_Picture_Woman", slot="M_Picture")
    for x in (120, 360):
        mesh("SM_CeilingLamp", (x, 0, 280), folder="Hallway/Props")
    mesh("SM_Rug_Runner", (240, 0, 0), folder="Hallway/Props")
    mesh("SM_Rug_Runner", (390, 0, 0), folder="Hallway/Props")

    # Warm, dim light like the concept: two ceiling lamps, two sconces, a cold fill through the windows.
    point_light("Light_Lamp_1", (120, 0, 250), 900, 700)
    point_light("Light_Lamp_2", (360, 0, 250), 900, 700)
    point_light("Light_Sconce_L", (490, -150, 195), 300, 350, shadows=False)
    point_light("Light_Sconce_R", (490, 150, 195), 300, 350, shadows=False)
    point_light("Light_Window_Fill", (560, 0, 170), 600, 500, color=(200, 215, 255), shadows=False)
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 400))
    sky.set_folder_path("Lighting")
    sky_component = sky.get_editor_property("light_component")
    sky_component.set_editor_property("intensity", 0.3)

    # Fixed exposure so the preview looks the same every time.
    ppv = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_editor_property("unbound", True)
    settings = ppv.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 7.8)
    ppv.set_editor_property("settings", settings)

    start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(40, 0, 100))
    start.set_folder_path("Player")

    level_editor.save_current_level()
    unreal.log("Hello Guest: hallway art preview at " + MAP_PATH)


build()
