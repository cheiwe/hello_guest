"""
Review level for the attic, basement and player room kits: /Game/Maps/Preview/L_Art_KitsPreview,
four corners arranged like their concepts, each with its own light.

    py Scripts/Tools/ue_run.py Scripts/Editor/create_art_preview_kits.py

    X = 0     attic radio station (Attic_Radio), puzzle parts set from RadioStation_sockets.json
    X = 700   secret basement desk (Secret_Basement)
    X = 1400  fuse basement (Basement_Fusebox)
    X = 2100  player's room (Player_Room)

Positions are written in Blender metres (the kits are modelled there) and converted by ue(): Unreal
mirrors Blender's Y, so y flips and yaw changes sign. Furniture faces -X, wall things face +Y.
"""

import json
import os

import unreal

MAP_PATH = "/Game/Maps/Preview/L_Art_KitsPreview"
ART = "/Game/Art/"
PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOCKETS = os.path.join(PROJECT, "SourceArt", "Models", "Attic", "RadioStation_sockets.json")

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def open_clean_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        level_editor.load_level(MAP_PATH)
        old = [a for a in actors.get_all_level_actors() if not isinstance(a, (unreal.WorldSettings, unreal.Brush))]
        actors.destroy_actors(old)
    else:
        level_editor.new_level(MAP_PATH)


def ue(loc, origin=(0, 0, 0)):
    """Blender metres -> Unreal centimetres, plus an Unreal-space origin for the corner."""
    return unreal.Vector(origin[0] + loc[0] * 100, origin[1] - loc[1] * 100, origin[2] + loc[2] * 100)


def mesh(path, loc, origin, yaw=0.0, roll=0.0, pitch=0.0, folder="Kits", material=None, slot=None):
    """Places /Game/Art/<path> at a Blender-space location; yaw/roll/pitch are Blender degrees."""
    actor = actors.spawn_actor_from_object(unreal.load_asset(ART + path), ue(loc, origin),
                                           unreal.Rotator(roll=-roll, pitch=pitch, yaw=-yaw))
    actor.set_folder_path(folder)
    if material:
        component = actor.get_editor_property("static_mesh_component")
        component.set_material(component.get_material_index(slot), unreal.load_asset(ART + "Materials/" + material))
    return actor


def point_light(label, loc, origin, intensity, radius, color, shadows=True):
    light = actors.spawn_actor_from_class(unreal.PointLight, ue(loc, origin))
    light.set_actor_label(label)
    light.set_folder_path("Lighting")
    c = light.get_editor_property("point_light_component")
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", intensity)
    c.set_editor_property("attenuation_radius", radius)
    c.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    c.set_editor_property("cast_shadows", shadows)
    return light


def floor(origin, tile, size=(5, 4), folder="Kits"):
    """Tiles under a corner; tile is (mesh path, tile size in m, pivot at the tile centre or corner)."""
    path, step, centred = tile
    for i in range(size[0]):
        for j in range(size[1]):
            x = (i - size[0] / 2 + (0.5 if centred else 0)) * step
            y = (j - size[1] / 2 + (0.5 if centred else 0)) * step
            mesh(path, (x, y, 0), origin, folder=folder)


def attic(o):
    f = "Attic"
    floor(o, ("Hallway/SM_Floor_Planks_100", 1.0, True), (6, 4), folder=f + "/Floor")
    mesh("Attic/SM_RadioStation", (0, 1.0, 0), o, folder=f)
    sockets = json.load(open(SOCKETS, encoding="utf-8"))["sockets"]
    for s in sockets:
        x, y, z = s["location"]
        mesh("Attic/" + s["mesh"], (x, y + 1.0, z), o, roll=s["rotation"][0], folder=f + "/Puzzle")
    # Furniture faces -X; yaw 90 turns it to face -Y, into the corner.
    mesh("Attic/SM_Wardrobe_Attic", (-2.4, 0.4, 0), o, yaw=90, folder=f)
    for k, (z, tilt) in enumerate(((0.6, 12), (1.05, -15), (1.55, 8))):
        mesh("Attic/SM_Board_Nailed_150", (-2.4, 0.4 - 0.36, z), o, yaw=90, roll=tilt, folder=f)
    mesh("Attic/SM_Dresser_Attic", (-1.6, 0.6, 0), o, yaw=90, folder=f)
    mesh("Attic/SM_Transformer_Old", (-0.6, -0.6, 0), o, folder=f)
    mesh("Attic/SM_Papers_Floor", (-1.2, -0.6, 0), o, folder=f)
    mesh("Props/SM_Box_Open_A", (1.9, -0.4, 0), o, yaw=20, folder=f)
    mesh("Attic/SM_Cables_Floor", (0.2, -0.3, 0), o, yaw=-20, folder=f)
    mesh("Attic/SM_Attic_Beam_400", (-2.0, 0.0, 2.9), o, folder=f + "/Timber")
    mesh("Attic/SM_Attic_Post_240", (-1.0, 1.2, 1.2), o, folder=f + "/Timber")
    point_light("Attic_Warm", (0.3, -1.0, 2.2), o, 500, 600, (255, 190, 120))
    point_light("Attic_Console", (0.4, 0.0, 1.4), o, 120, 250, (255, 160, 80), shadows=False)


def secret(o):
    f = "SecretBasement"
    floor(o, ("Basement/SM_Floor_Concrete_200", 2.0, False), (3, 2), folder=f + "/Floor")
    mesh("Basement/SM_Desk_Old", (0, 0, 0), o, folder=f)
    mesh("Basement/SM_Mixer", (-0.15, -0.35, 0.76), o, folder=f)
    mesh("Basement/SM_Mixer", (-0.15, 0.15, 0.76), o, folder=f)
    mesh("Basement/SM_Keyboard_Old", (-0.25, 0.25, 0.76), o, yaw=5, folder=f)
    mesh("Basement/SM_Mouse_Old", (-0.25, 0.6, 0.76), o, folder=f)
    mesh("Basement/SM_CRT_Monitor_Large", (0.05, -0.45, 0.88), o, folder=f)
    mesh("Basement/SM_CRT_Monitor_Recording", (0.05, 0.1, 0.88), o, folder=f)
    mesh("Basement/SM_CRT_Monitor", (0.05, -0.45, 1.38), o, yaw=-5, folder=f)
    mesh("Basement/SM_CRT_Monitor", (-0.05, 0.55, 0.76), o, yaw=10, folder=f)
    mesh("Basement/SM_DeskLamp_Red", (0.1, 0.45, 1.3), o, folder=f)
    mesh("Basement/SM_VCR", (-0.1, -0.95, 0.0), o, folder=f)
    mesh("Basement/SM_VCR", (-0.1, -0.95, 0.09), o, folder=f)
    mesh("Basement/SM_VHS_Stack", (-0.1, -0.95, 0.18), o, folder=f)
    mesh("Basement/SM_VHS_Floor", (-0.6, -0.4, 0), o, folder=f)
    mesh("Basement/SM_OfficeChair", (-0.85, 0.5, 0), o, yaw=-30, folder=f)
    mesh("Basement/SM_PC_Tower", (0.0, 0.25, 0), o, folder=f)
    mesh("Basement/SM_Stairs_Concrete", (-2.5, 1.0, 0), o, yaw=90, folder=f)
    point_light("Secret_RedLamp", (-0.1, 0.45, 1.2), o, 400, 450, (255, 40, 30))
    point_light("Secret_Screens", (-0.6, 0.0, 1.1), o, 120, 300, (200, 215, 255), shadows=False)


def fuse(o):
    f = "FuseBasement"
    floor(o, ("Basement/SM_Floor_Concrete_200", 2.0, False), (3, 2), folder=f + "/Floor")
    for k in range(2):
        mesh("Basement/SM_Wall_Brick_200", (-2.0 + k * 2, 1.0, 0), o, folder=f + "/Walls")
    # Wall things are built facing -Y with the back at Y=0; the wall face is at Y=1.0 here.
    # Fuse box doors: hinge at the outer edge; the left one closed, the right one swung open.
    mesh("Basement/SM_FuseBox", (0.0, 1.0, 1.1), o, folder=f)
    mesh("Basement/SM_FuseBox_Door", (-0.31, 0.8, 1.1), o, folder=f)
    mesh("Basement/SM_FuseBox_Door", (0.31, 0.8, 1.1), o, yaw=-100, folder=f)
    mesh("Basement/SM_KnifeSwitch", (0.95, 1.0, 1.3), o, folder=f)
    mesh("Basement/SM_KnifeSwitch_Lever", (0.95, 0.83, 1.34), o, folder=f)
    mesh("Basement/SM_Fuse", (-0.6, -0.6, 0), o, folder=f)
    mesh("Basement/SM_WaterHeater", (-1.6, 0.6, 0), o, folder=f)
    mesh("Basement/SM_Sheet_Armchair", (-0.6, -0.2, 0), o, yaw=30, folder=f)
    mesh("Basement/SM_Sheet_Cabinet", (-2.5, -0.5, 0), o, yaw=90, folder=f)
    mesh("Basement/SM_Chair_Wood_Old", (-1.7, -0.6, 0), o, yaw=-40, folder=f)
    mesh("Basement/SM_Puddle_Large", (0.4, -0.4, 0), o, folder=f)
    mesh("Basement/SM_Puddle_Small", (-0.9, -1.1, 0), o, folder=f)
    mesh("Basement/SM_Pipes_Ceiling_400", (-2.0, 0.3, 2.6), o, folder=f)
    mesh("Props/SM_Box_Closed_B", (0.9, 0.5, 0), o, folder=f)
    point_light("Fuse_Bulb", (0.0, -0.5, 2.3), o, 300, 500, (150, 200, 210))
    point_light("Fuse_Spark", (0.45, 0.85, 1.25), o, 60, 120, (255, 170, 90), shadows=False)


def player_room(o):
    f = "PlayerRoom"
    floor(o, ("Hallway/SM_Floor_Planks_100", 1.0, True), (6, 4), folder=f + "/Floor")
    # Back wall along X at Y=2 (Blender); the room is on the -Y side. Wall things already face -Y,
    # furniture (faces -X) is turned by yaw 90.
    mesh("PlayerRoom/SM_Bed_Player", (-1.2, 1.45, 0), o, yaw=180, folder=f)
    mesh("PlayerRoom/SM_Window_Sash_150", (-1.3, 2.0, 0.9), o, yaw=0, folder=f)
    mesh("PlayerRoom/SM_Bookcase_Player", (0.4, 1.83, 0), o, yaw=90, folder=f)
    mesh("PlayerRoom/SM_Boombox", (0.45, 1.8, 1.27), o, yaw=90, folder=f)
    mesh("PlayerRoom/SM_Toy_Robot", (0.3, 1.85, 1.27), o, yaw=90, folder=f)
    mesh("PlayerRoom/SM_Radio_Tube", (0.0, 1.0, 0), o, yaw=-110, folder=f)
    mesh("PlayerRoom/SM_Clothes_Pile", (1.0, 1.2, 0), o, folder=f)
    mesh("PlayerRoom/SM_Desk_Player", (2.0, 1.65, 0), o, yaw=90, folder=f)
    mesh("PlayerRoom/SM_Chair_Tube", (2.0, 1.05, 0), o, yaw=-70, folder=f)
    mesh("PlayerRoom/SM_CorkBoard", (2.1, 2.0, 1.45), o, folder=f)
    mesh("Props/SM_DeskLamp", (1.7, 1.8, 0.76), o, yaw=90, folder=f)
    mesh("PlayerRoom/SM_Mug", (1.65, 1.5, 0.76), o, folder=f)
    mesh("PlayerRoom/SM_Books_Stack", (2.45, 1.7, 0.76), o, folder=f)
    mesh("PlayerRoom/SM_Rug_Player", (0.6, 0.4, 0), o, folder=f)
    mesh("PlayerRoom/SM_Comics_Floor", (-0.2, 0.0, 0.012), o, folder=f)
    mesh("PlayerRoom/SM_WasteBin", (2.9, 1.7, 0), o, folder=f)
    for i, k in enumerate(("Beats", "AstroBoy", "Robot", "Attack")):
        mesh("PlayerRoom/SM_Poster_" + k, (0.1 + i * 0.5, 2.0, 1.75), o, folder=f + "/Posters")
    point_light("Room_Lamp", (1.6, 1.5, 1.2), o, 500, 600, (255, 200, 130))
    point_light("Room_Sunset", (-1.3, 1.0, 1.8), o, 500, 600, (255, 170, 110), shadows=False)


def build():
    open_clean_level()
    attic((0, 0, 0))
    secret((700, 0, 0))
    fuse((1400, 0, 0))
    player_room((2100, 0, 0))
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_folder_path("Lighting")
    sky.get_editor_property("light_component").set_editor_property("intensity", 0.15)
    ppv = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_editor_property("unbound", True)
    settings = ppv.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 7.8)
    ppv.set_editor_property("settings", settings)
    start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 300, 100))
    start.set_folder_path("Player")
    level_editor.save_current_level()
    unreal.log("Hello Guest: kits preview at " + MAP_PATH)


build()
