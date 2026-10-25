"""
Review level for the outdoor and yard kits: /Game/Maps/Preview/L_Art_StreetPreview, a stretch of
street like Street_Example: road, curbs and sidewalks, the player's house on one side, the overgrown
yard with oaks, the rusty van and junk on the other, the UFO with its beam and the ray gun above.
Sunset light with auto exposure.

    py Scripts/Tools/ue_run.py Scripts/Editor/create_art_preview_street.py

Positions are Blender metres (+Y = the player's side of the street), converted like in
create_art_preview_kits.py: Unreal mirrors Y, so y flips and yaw changes sign.
"""

import random

import unreal

MAP_PATH = "/Game/Maps/Preview/L_Art_StreetPreview"
ART = "/Game/Art/"

level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def open_clean_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        level_editor.load_level(MAP_PATH)
        old = [a for a in actors.get_all_level_actors() if not isinstance(a, (unreal.WorldSettings, unreal.Brush))]
        actors.destroy_actors(old)
    else:
        level_editor.new_level(MAP_PATH)


def ue(loc):
    return unreal.Vector(loc[0] * 100, -loc[1] * 100, loc[2] * 100)


def mesh(path, loc, yaw=0.0, pitch=0.0, roll=0.0, scale=1.0, folder="Street", material=None):
    actor = actors.spawn_actor_from_object(unreal.load_asset(ART + path), ue(loc), unreal.Rotator(roll=-roll, pitch=pitch, yaw=-yaw))
    actor.set_folder_path(folder)
    if scale != 1.0:
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    if material:
        component = actor.get_editor_property("static_mesh_component")
        for i in range(component.get_num_materials()):
            component.set_material(i, unreal.load_asset(ART + "Materials/" + material))
    return actor


def build():
    open_clean_level()
    rnd = random.Random(4)
    # Ground: 4 m tiles of the concrete floor piece with the forest-ground look.
    for i in range(-6, 6):
        for j in range(-6, 5):
            if -1 <= j <= 0:
                continue                     # the road strip
            mesh("Basement/SM_Floor_Concrete_200", (i * 4, j * 4, -0.02), scale=2.0, folder="Ground", material="MI_Ground")
    # Road, curbs and sidewalks along X.
    for i in range(-6, 6):
        x = i * 4
        mesh("Outdoor/SM_Road_400", (x, 0, 0), folder="Street/Road")
        mesh("Outdoor/SM_Curb_400", (x, 3.5, 0), folder="Street/Road")
        mesh("Outdoor/SM_Curb_400", (x + 4, -3.5, 0), yaw=180, folder="Street/Road")
        mesh("Outdoor/SM_Sidewalk_400", (x, 3.68, 0), folder="Street/Road")
        mesh("Outdoor/SM_Sidewalk_400", (x + 4, -3.68, 0), yaw=180, folder="Street/Road")
    # Player's side (+Y): the cottage, a street tree, hedge, mailbox.
    mesh("Yard/SM_PlayerHouse", (-6, 8.0, 0), folder="Street/PlayerSide")
    mesh("Outdoor/SM_Tree_Street", (2.5, 7.0, 0), folder="Street/PlayerSide")
    mesh("Outdoor/SM_Mailbox", (-4.5, 5.9, 0), yaw=-90, folder="Street/PlayerSide")
    for k in range(4):
        mesh("Outdoor/SM_Hedge_200", (-12 + k * 2.2, 5.8, 0), folder="Street/PlayerSide")
    mesh("Outdoor/SM_Bush_A", (-1.5, 6.5, 0), folder="Street/PlayerSide")
    # The Guest's side (-Y): overgrown yard behind a plank fence, oaks, van, junk.
    for k in range(9):
        mesh("Exterior/SM_Fence_Plank_200", (-8 + k * 2, -6.0, 0), folder="Street/Yard")
    mesh("Outdoor/SM_Tree_Oak_A", (-3.0, -13.0, 0), yaw=40, folder="Street/Yard")
    mesh("Outdoor/SM_Tree_Oak_B", (7.5, -15.0, 0), yaw=200, folder="Street/Yard")
    mesh("Outdoor/SM_Tree_Dead", (11.0, -9.0, 0), yaw=90, folder="Street/Yard")
    mesh("Outdoor/SM_Van", (5.0, -9.0, 0), yaw=-25, folder="Street/Yard")
    mesh("Outdoor/SM_Van_SideDoor", (5.0, -9.0, 0), yaw=-25, folder="Street/Yard")
    for name, loc, yaw in (("Yard/SM_Barrel_Rust", (-1.0, -8.0, 0), 0), ("Yard/SM_Barrel_Rust", (-0.3, -8.4, 0), 30), ("Yard/SM_Barrel_Rust_Lying", (1.2, -9.5, 0), 60),
                           ("Yard/SM_Firewood_Pile", (-5.0, -7.0, 0), 0), ("Yard/SM_Wheelbarrow", (2.0, -11.5, 0), 140), ("Yard/SM_Hose_Coil", (0.5, -10.5, 0), 0),
                           ("Yard/SM_Stump", (-6.5, -10.0, 0), 0), ("Yard/SM_Planks_Heap", (-2.5, -9.5, 0), 20), ("Props/SM_Crate_Wood", (3.0, -7.2, 0), 15)):
        mesh(name, loc, yaw=yaw, folder="Street/Yard")
    for k in range(6):
        mesh(rnd.choice(("Outdoor/SM_Bush_A", "Outdoor/SM_Bush_B")), (rnd.uniform(-10, 10), rnd.uniform(-16, -7), 0), yaw=rnd.uniform(0, 360), folder="Street/Yard")
    for k in range(60):
        mesh(rnd.choice(("Outdoor/SM_Grass_Tuft_A", "Outdoor/SM_Grass_Tuft_B")), (rnd.uniform(-14, 14), rnd.uniform(-16, -6.5), 0), yaw=rnd.uniform(0, 360), folder="Street/Grass")
    # The UFO over the yard, its beam and the ray gun hanging in it.
    mesh("Outdoor/SM_UFO", (0, -11.0, 11.0), folder="Street/UFO")
    mesh("Outdoor/SM_UFO_Beam", (0, -11.0, 11.0 - 0.72), folder="Street/UFO")
    mesh("Outdoor/SM_RayGun", (0, -11.0, 5.0), yaw=30, roll=-15, scale=2.0, folder="Street/UFO")

    # Sunset: low warm sun, sky and atmosphere, a little fog; auto exposure.
    sun = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(roll=0, pitch=-12, yaw=-140))
    sun.set_folder_path("Lighting")
    sc = sun.get_editor_property("directional_light_component")
    sc.set_editor_property("intensity", 6.0)
    sc.set_editor_property("light_color", unreal.Color(r=255, g=190, b=130, a=255))
    sc.set_editor_property("atmosphere_sun_light", True)
    for cls in (unreal.SkyAtmosphere, unreal.ExponentialHeightFog):
        a = actors.spawn_actor_from_class(cls, unreal.Vector(0, 0, 0))
        a.set_folder_path("Lighting")
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_folder_path("Lighting")
    skc = sky.get_editor_property("light_component")
    skc.set_editor_property("real_time_capture", True)
    skc.set_editor_property("intensity", 1.0)
    glow = actors.spawn_actor_from_class(unreal.PointLight, ue((0, -11.0, 3.0)))
    glow.set_folder_path("Lighting")
    gc = glow.get_editor_property("point_light_component")
    gc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    gc.set_editor_property("intensity", 6000)
    gc.set_editor_property("attenuation_radius", 1200)
    gc.set_editor_property("light_color", unreal.Color(r=110, g=255, b=120, a=255))
    start = actors.spawn_actor_from_class(unreal.PlayerStart, ue((-6, 4.5, 1.0)))
    start.set_folder_path("Player")
    level_editor.save_current_level()
    unreal.log("Hello Guest: street preview at " + MAP_PATH)


build()
