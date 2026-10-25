"""
Builds /Game/Maps/L_Act1_Art: Act 1 with the art kits on top of the blockout, at night in a
thunderstorm, with the finale (Vitec_Play).

    py Scripts/Tools/ue_run.py Scripts/Editor/create_act1_art.py

How it works:
1. Runs the blockout (create_act1_house.py) into this map, so the layout and all gameplay (doors,
   locks, obstacles, pickups, zones, navigation, the Guest, patrol points) are exactly the same.
   The blockout cubes get world-aligned art materials (MI_Arch_*) instead of the grey colours.
2. Lines the cubes where one material per cube is not enough: wallpaper inside the outer walls,
   brick and concrete in the basements, boards under the roof, plaster ceilings.
3. Replaces the blue prop blocks with art meshes. The blocks stay as invisible colliders, so hiding
   places and climbing are unchanged.
4. Street, the player's house, yards, the van; night, rain, lightning, thunder (AHGStorm).
5. Finale: Vitec at the console of the closed basement, the cutscene sequence, subtitles and the
   CCTV "recording" of the Guest dragging the neighbour into the van (AHGFinaleTrigger).

Re-running rebuilds the map from scratch. Change the architecture in create_act1_house.py and run
this script again; everything here is placed relative to the blockout's numbers.
"""

import math
import os
import random

import unreal

PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
BLOCKOUT_SCRIPT = os.path.join(PROJECT, "Scripts", "Editor", "create_act1_house.py")
MAP_PATH = "/Game/Maps/L_Act1_Art"
ART = "/Game/Art/"
MATS = ART + "Materials/"
SEQ_DIR = "/Game/Maps/Act1"

src = open(BLOCKOUT_SCRIPT, encoding="utf-8").read().replace("\nbuild()\n", "\n")
B = {"__name__": "act1_blockout"}
exec(src, B)
B["MAP_PATH"] = MAP_PATH

actors = B["actors"]
level_editor = B["level_editor"]
F1, F2, ATTIC, EAVE, RIDGE, T = B["F1"], B["F2"], B["ATTIC"], B["EAVE"], B["RIDGE"], B["T"]
FUSE_BASEMENT, CLOSED_BASEMENT, FOUNDATION, GROUND = B["FUSE_BASEMENT"], B["CLOSED_BASEMENT"], B["FOUNDATION"], B["GROUND"]
HOUSE_DEPTH, HALF_WIDTH = B["HOUSE_DEPTH"], B["HALF_WIDTH"]

# --- Materials for the blockout cubes ------------------------------------------------------------

KIND_LOOK = {
    "Ground": "Arch_Ground", "Street": "Arch_Asphalt", "Wall": "Arch_Wallpaper", "Exterior": "Arch_Siding",
    "Floor": "Arch_WoodFloor", "Stairs": "Arch_WoodDark", "Roof": "Arch_Shingle", "Ledge": "Arch_Trim",
    "Prop": "Arch_WoodDark", "Boards": "Arch_WoodWeathered", "Fence": "Arch_WoodWeathered",
    "ChainLink": "Arch_ChainLink", "Hazard": "Arch_WoodDark", "PlayerHouse": "Arch_SidingCream",
}
_mats = {}


def mat(look):
    if look not in _mats:
        _mats[look] = unreal.load_asset(MATS + "MI_" + look)
    return _mats[look]


def art_material(kind):
    """Replaces the blockout's colour per kind; an Arch_* name can be passed directly."""
    return mat(kind if kind.startswith("Arch_") else KIND_LOOK[kind])


B["blockout_material"] = art_material


# --- Helpers -------------------------------------------------------------------------------------

def find(label):
    for a in actors.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def find_prefix(prefix):
    return [a for a in actors.get_all_level_actors() if a.get_actor_label().startswith(prefix)]


def cube_box(actor):
    """(x1, x2, y1, y2, z1, z2) of an unrotated blockout cube."""
    loc = actor.get_actor_location()
    s = actor.get_actor_scale3d()
    return (loc.x - s.x * 50, loc.x + s.x * 50, loc.y - s.y * 50, loc.y + s.y * 50, loc.z - s.z * 50, loc.z + s.z * 50)


def set_look(actor, look):
    actor.get_editor_property("static_mesh_component").set_material(0, mat(look))


def mesh(path, loc, yaw=0.0, folder="Art", scale=None, pitch=0.0, roll=0.0, collision=True, label=None, material=None, slot=None):
    actor = actors.spawn_actor_from_object(unreal.load_asset(ART + path), unreal.Vector(*loc), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
    actor.set_folder_path(folder)
    if label:
        actor.set_actor_label(label)
    if scale is not None:
        actor.set_actor_scale3d(unreal.Vector(*scale) if isinstance(scale, (tuple, list)) else unreal.Vector(scale, scale, scale))
    component = actor.get_editor_property("static_mesh_component")
    if not collision:
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_editor_property("can_ever_affect_navigation", False)
    if material:
        index = 0 if slot is None else component.get_material_index(slot)
        component.set_material(index, mat(material))
    return actor


def local_to_world(origin, yaw, local_blender):
    """A point given in a kit's Blender metres relative to its pivot -> Unreal world (Y mirrored)."""
    lx, ly, lz = local_blender[0] * 100, -local_blender[1] * 100, local_blender[2] * 100
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return (origin[0] + lx * c - ly * s, origin[1] + lx * s + ly * c, origin[2] + lz)


def dress(label, path, yaw=0.0, dz=0.0, dx=0.0, dy=0.0, scale=None, folder="Art/Props", remove=False, **kw):
    """Art mesh standing on the floor in the middle of a blockout block; the block becomes an
    invisible collider (or is removed when the art mesh should collide itself)."""
    block = find(label)
    if block is None:
        unreal.log_warning("Hello Guest art: no block %s" % label)
        return None
    x1, x2, y1, y2, z1, z2 = cube_box(block)
    art = mesh(path, ((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, z1 + dz), yaw, folder, scale, collision=remove, **kw)
    if remove:
        actors.destroy_actor(block)
    else:
        component = block.get_editor_property("static_mesh_component")
        component.set_visibility(False)
        component.set_editor_property("cast_shadow", False)
    return art


def point_light(label, loc, lumens, radius, color, shadows=False, folder="Lighting"):
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc))
    light.set_actor_label(label)
    light.set_folder_path(folder)
    c = light.get_editor_property("point_light_component")
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", lumens)
    c.set_editor_property("attenuation_radius", radius)
    c.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    c.set_editor_property("cast_shadows", shadows)
    return light


# --- 1. Night environment instead of the blockout's evening sun ----------------------------------

def night_environment():
    """Moonlight through storm clouds, the sky dome, fog; ground, street and the safe zone as in
    the blockout (the player's house is the art cottage)."""
    moon = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2000), unreal.Rotator(roll=0, pitch=-38, yaw=-120))
    moon.set_actor_label("Moon")
    moon.set_folder_path("Lighting")
    mc = moon.get_editor_property("directional_light_component")
    mc.set_editor_property("intensity", 0.35)
    mc.set_editor_property("light_color", unreal.Color(r=140, g=160, b=215, a=255))
    # The moon drives fog and translucency; the storm's lightning light has priority 0.
    mc.set_editor_property("forward_shading_priority", 1)
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500))
    sky.set_actor_label("SkyLight")
    sky.set_folder_path("Lighting")
    sc = sky.get_editor_property("light_component")
    # Captures the scene with the cloud dome (real-time capture would need a SkyAtmosphere).
    sc.set_editor_property("real_time_capture", False)
    sc.set_editor_property("source_type", unreal.SkyLightSourceType.SLS_CAPTURED_SCENE)
    sc.set_editor_property("intensity", 0.6)
    fog = actors.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    fog.set_actor_label("StormFog")
    fog.set_folder_path("Lighting")
    fc = fog.get_editor_property("component")
    fc.set_editor_property("fog_density", 0.035)
    fc.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.012, 0.015, 0.022, 1))
    dome = mesh("Outdoor/SM_SkyDome", (0, 0, -2000), folder="Lighting", collision=False, label="SkyDome")
    dome.get_editor_property("static_mesh_component").set_editor_property("cast_shadow", False)
    # Fixed exposure: the night must stay dark, the lit rooms bright.
    ppv = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_actor_label("NightPostProcess")
    ppv.set_folder_path("Lighting")
    ppv.set_editor_property("unbound", True)
    st = ppv.get_editor_property("settings")
    st.set_editor_property("override_auto_exposure_method", True)
    st.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    st.set_editor_property("override_auto_exposure_bias", True)
    st.set_editor_property("auto_exposure_bias", 8.4)
    st.set_editor_property("override_vignette_intensity", True)
    st.set_editor_property("vignette_intensity", 0.55)
    st.set_editor_property("override_film_grain_intensity", True)
    st.set_editor_property("film_grain_intensity", 0.15)
    ppv.set_editor_property("settings", st)

    w = HALF_WIDTH
    for index, rect in enumerate(B["subtract_rect"]([(-3500, 4000, -2500, 2500)], (0, HOUSE_DEPTH, -w, w))):
        B["block"]("Ground_%d" % index, rect[0], rect[1], rect[2], rect[3], GROUND - 20, GROUND, "Exterior", "Ground")
    B["block"]("Path", -700, -300, -100, 100, GROUND, GROUND + 2, "Exterior", "Arch_Concrete")
    start = B["spawn"](unreal.PlayerStart, (-1800, 0, 100), label="HomeSpawn", folder="Player")
    start.set_editor_property("player_start_tag", "HomeSpawn")
    B["safe_zone"]("SafeZone_PlayerSide", -3500, -1100, -2500, 2500, GROUND - 100, 1000)


B["build_environment"] = night_environment


# --- 2. Materials by place, linings ----------------------------------------------------------------

def zone_material(box):
    """Look for an interior surface from where it is in the house."""
    x1, x2, y1, y2, z1, z2 = box
    zc, xc, yc = (z1 + z2) / 2, (x1 + x2) / 2, (y1 + y2) / 2
    if zc < F1 - T:
        return "Arch_Brick" if (550 <= xc <= 1250 and yc < -75) else "Arch_ConcreteDamp"
    if zc > ATTIC:
        return "Arch_WoodWorn"
    if zc > F2:
        return "Arch_WallpaperStripe" if (xc > 1250 and yc < -75) else "Arch_Wallpaper"
    return "Arch_Wallpaper"


def retexture():
    for a in actors.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor):
            continue
        label = a.get_actor_label()
        folder = str(a.get_folder_path())
        box = cube_box(a)
        if folder == "Geometry/Walls":
            set_look(a, zone_material(box))
        elif label.startswith(("Floor_FuseBasement", "Floor_ClosedBasement", "Foundation_")):
            set_look(a, "Arch_Concrete")
        elif label.startswith("Floor_Attic"):
            set_look(a, "Arch_WoodWorn")
        elif label.startswith("Stairs_ClosedBasement"):
            set_look(a, "Arch_Concrete")    # the false step looks like the others
        elif label.startswith("Spire"):
            set_look(a, "Arch_MetalDark")
        elif label in ("Attic_WeakFloor", "Radio_RedBox", "ClosedBasement_Monitors"):
            a.get_editor_property("static_mesh_component").set_visibility(False)
        elif label == "BulbRoom_RedNumbers":
            a.get_editor_property("static_mesh_component").set_material(0, mat("PaintRed"))


def line(label, x1, x2, y1, y2, z1, z2, look):
    B["block"](label, x1, x2, y1, y2, z1, z2, "Geometry/Lining", look)


BANDS = ((FOUNDATION, F1 - T), (F1, F2 - T), (F2, ATTIC - T), (ATTIC, EAVE))


def add_linings():
    """Inside faces of the outer walls and gables, ceilings, the underside of the roof."""
    inner = {"Ext_Front": (+1, "x"), "Ext_Back": (-1, "x"), "Ext_Left": (+1, "y"), "Ext_Right": (-1, "y")}
    for prefix, (sign, axis) in inner.items():
        for a in find_prefix(prefix + "_"):
            x1, x2, y1, y2, z1, z2 = cube_box(a)
            for k, (b1, b2) in enumerate(BANDS):
                lo, hi = max(z1, b1), min(z2, b2)
                if hi - lo < 1:
                    continue
                look = zone_material((x1, x2, y1, y2, lo, hi))
                if axis == "x":
                    face = x2 if sign > 0 else x1
                    line("%s_Lin%d" % (a.get_actor_label(), k), face, face + sign * 1.0, y1, y2, lo, hi, look)
                else:
                    face = y2 if sign > 0 else y1
                    line("%s_Lin%d" % (a.get_actor_label(), k), x1, x2, face, face + sign * 1.0, lo, hi, look)
    for prefix, sign in (("Gable_Front", +1), ("Gable_Back", -1)):
        for a in find_prefix(prefix + "_"):
            x1, x2, y1, y2, z1, z2 = cube_box(a)
            face = x2 if sign > 0 else x1
            line(a.get_actor_label() + "_Lin", face, face + sign * 1.0, y1 + 2, y2 - 2, z1, z2, "Arch_WoodWorn")
    # Ceilings under the slabs: plaster upstairs, concrete in the basements.
    for prefix, look in (("Floor_F1_", "Arch_Concrete"), ("Floor_F2_", "Arch_Plaster"), ("Floor_Attic_", "Arch_Plaster")):
        for a in find_prefix(prefix):
            x1, x2, y1, y2, z1, z2 = cube_box(a)
            line(a.get_actor_label() + "_Ceil", x1, x2, y1, y2, z1 - 1.0, z1, look)
    # Boards under the shingles (seen from the attic).
    for a in find_prefix("Roof_"):
        if a.get_actor_label().startswith("Roof_RidgeCap"):
            continue
        rot = a.get_actor_rotation()
        up = rot.get_up_vector()
        loc = a.get_actor_location()
        s = a.get_actor_scale3d()
        under = actors.spawn_actor_from_object(B["CUBE"], loc - up * (T / 2 + 1.0), rot)
        under.set_actor_label(a.get_actor_label() + "_Under")
        under.set_folder_path("Geometry/Lining")
        under.set_actor_scale3d(unreal.Vector(s.x, s.y, 0.02))
        under.get_editor_property("static_mesh_component").set_material(0, mat("Arch_WoodWorn"))
        under.get_editor_property("static_mesh_component").set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)


# --- 3. Doors, obstacles and props -----------------------------------------------------------------

def dress_doors():
    panel = unreal.load_asset(ART + "Hallway/SM_Door_Panel")
    for door in actors.get_all_level_actors():
        if door.get_class().get_name() != "HGDoor":
            continue
        component = door.get_editor_property("mesh")
        component.set_static_mesh(panel)
        # The cube placeholder is 10 x 100 x 210 cm with its edge on the hinge; the panel is 118 x 248.
        component.set_editor_property("relative_scale3d", unreal.Vector(0.6, 100.0 / 118.0, 210.0 / 248.0))
        component.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
    chained = find("ChainedDoor")
    if chained:
        hinge = chained.get_editor_property("hinge")
        chains = mesh("Hallway/SM_ChainedDoor_Chains", (0, 0, 0), folder="Doors", collision=False)
        chains.attach_to_component(hinge, unreal.Name(), unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
        for y, z, look in ((35, 178, "PaintRed"), (95, 169, "PaintYellow"), (55, 88, "PaintBlue"), (74, 165, None)):
            lock = mesh("Hallway/SM_Padlock_Big" if look is None else "Hallway/SM_Padlock", (0, 0, 0), folder="Doors", collision=False,
                        material=look)
            lock.attach_to_component(hinge, unreal.Name(), unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
            lock.set_actor_relative_location(unreal.Vector(-8, y, z), False, False)
    for obstacle in actors.get_all_level_actors():
        if obstacle.get_class().get_name() != "HGObstacle":
            continue
        label = obstacle.get_actor_label()
        component = obstacle.get_editor_property("mesh")
        if label == "SpiderWeb":
            component.set_static_mesh(unreal.load_asset(ART + "Hallway/SM_SpiderWeb"))
            component.set_editor_property("relative_scale3d", unreal.Vector(1, 1, 1))
            component.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
        elif label == "PoliceTape":
            component.set_static_mesh(unreal.load_asset(ART + "Rooms/SM_CautionTape_Cross"))
            component.set_editor_property("relative_rotation", unreal.Rotator(roll=0, pitch=0, yaw=90))
            component.set_editor_property("relative_scale3d", unreal.Vector(1.0 / obstacle.get_actor_scale3d().y, 1, 1.0 / obstacle.get_actor_scale3d().z))
            component.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
        else:
            component.set_material(0, mat("Arch_WoodWeathered"))


def dress_props():
    f1, f2, at = "Art/F1", "Art/F2", "Art/Attic"
    # Hallway and vestibule (Hallway_01/02).
    dress("Hall_CoatRack", "Hallway/SM_CoatRack", folder=f1)
    dress("Hall_PhoneTable", "Hallway/SM_PhoneTable", yaw=90, folder=f1)
    mesh("Hallway/SM_RotaryPhone", (1200, 130, F1 + 80), 90, f1, collision=False)
    for x in (260, 600, 900):
        mesh("Hallway/SM_Rug_Runner", (x, 0, F1), 0, f1, collision=False)
    for x, y, yaw in ((150, -66, 0), (420, 66, 180), (800, -66, 0)):
        mesh("Hallway/SM_PhotoFrame", (x, y, F1 + 160), yaw, f1, collision=False)
    for x, y, yaw in ((1240, -160, 0), (1240, 160, 180)):
        mesh("Hallway/SM_WallSconce", (x, y, F1 + 190), yaw, f1, collision=False)
    # Storage (Workshop_with_crowds).
    dress("Storage_Table", "Props/SM_Workbench", folder=f1)
    dress("Storage_Cabinet", "Props/SM_Shelving_Metal", yaw=90, folder=f1)
    for k, (x, y) in enumerate(((120, -150), (180, -120), (480, -150))):
        mesh("Props/SM_Box_Closed_A" if k % 2 else "Props/SM_Box_Open_A", (x, y, F1), 20 * k, f1)
    mesh("Props/SM_PaintCan_A", (300, -470, F1 + 85), 0, f1, collision=False)
    mesh("Props/SM_DeskLamp", (180, -450, F1 + 85), 30, f1, collision=False)
    # Study (Study_Puzzle).
    dress("Study_Desk", "Study/SM_Desk_Writing", yaw=90, folder=f1)
    dress("Study_Pedestal", "Study/SM_Pedestal_Marble", folder=f1)
    mesh("Study/SM_Globe", (470, 430, F1 + 110), 0, f1, collision=False)
    bookshelf = find("Study_Bookshelf")
    if bookshelf:
        bookshelf.get_editor_property("static_mesh_component").set_visibility(False)
        for y in (180, 310, 440):
            mesh("Study/SM_Bookcase_Tall", (40, y, F1), 180, f1, collision=False)
    mesh("Study/SM_Lamp_Bankers", (290, 450, F1 + 78), 90, f1, collision=False)
    mesh("Study/SM_Inkwell", (350, 420, F1 + 78), 0, f1, collision=False)
    # Kitchen and pantry: the counter stays a block, panelled.
    set_look(find("Kitchen_Counter"), "Arch_WoodPanel")
    dress("Dining_Table", "Rooms/SM_Desk_Cabriole", yaw=90, folder=f1)
    dress("Pantry_Shelf", "Props/SM_Shelving_Metal", yaw=90, folder=f1)
    # Fuse basement (Basement_Fusebox).
    fb = "Art/FuseBasement"
    dress("FuseBasement_Cabinet", "Basement/SM_Sheet_Cabinet", folder=fb)
    dress("FuseBasement_WaterHeater", "Basement/SM_WaterHeater", folder=fb)
    box_loc = (1250 - 10, -200, FUSE_BASEMENT + 100)
    mesh("Basement/SM_FuseBox", box_loc, 90, fb, collision=False)
    mesh("Basement/SM_FuseBox_Door", local_to_world(box_loc, 90, (-0.31, -0.2, 0)), 90, fb, collision=False)
    mesh("Basement/SM_FuseBox_Door", local_to_world(box_loc, 90, (0.31, -0.2, 0)), 90 - 100, fb, collision=False)
    sw = (1250 - 10, -40, FUSE_BASEMENT + 130)
    mesh("Basement/SM_KnifeSwitch", sw, 90, fb, collision=False)
    mesh("Basement/SM_KnifeSwitch_Lever", local_to_world(sw, 90, (0, -0.17, 0.04)), 90, fb, collision=False)
    mesh("Basement/SM_Pipes_Ceiling_400", (650, -300, F1 - T - 2), 0, fb, collision=False)
    mesh("Basement/SM_Pipes_Ceiling_400", (1050, -300, F1 - T - 2), 0, fb, collision=False, scale=(0.5, 1, 1))
    mesh("Basement/SM_Sheet_Armchair", (900, -150, FUSE_BASEMENT), 200, fb)
    mesh("Basement/SM_Chair_Wood_Old", (760, -420, FUSE_BASEMENT), 60, fb)
    mesh("Basement/SM_Puddle_Large", (950, -320, FUSE_BASEMENT), 30, fb, collision=False)
    mesh("Basement/SM_Puddle_Small", (700, -250, FUSE_BASEMENT), 0, fb, collision=False)
    mesh("Props/SM_Box_Closed_B", (1150, -120, FUSE_BASEMENT), 10, fb)
    # Closed basement (Secret_Basement): the console desk with its monitors, Vitec's corner.
    cb = "Art/SecretBasement"
    desk = find("ClosedBasement_Console")
    if desk:
        desk.get_editor_property("static_mesh_component").set_visibility(False)
    origin = (610, 300, CLOSED_BASEMENT)
    yaw = 180.0                                   # the desk faces +X, into the room
    for path, local, lyaw, coll in (
            ("Basement/SM_Desk_Old", (0, 0, 0), 0, False), ("Basement/SM_Mixer", (-0.15, -0.35, 0.76), 0, False),
            ("Basement/SM_Mixer", (-0.15, 0.15, 0.76), 0, False), ("Basement/SM_Keyboard_Old", (-0.25, 0.25, 0.76), 5, False),
            ("Basement/SM_Mouse_Old", (-0.25, 0.6, 0.76), 0, False), ("Basement/SM_CRT_Monitor_Large", (0.05, -0.45, 0.88), 0, False),
            ("Basement/SM_CRT_Monitor_Recording", (0.05, 0.1, 0.88), 0, False), ("Basement/SM_CRT_Monitor", (0.05, -0.45, 1.38), -5, False),
            ("Basement/SM_CRT_Monitor", (-0.05, 0.55, 0.76), 10, False), ("Basement/SM_DeskLamp_Red", (0.1, 0.45, 1.3), 0, False),
            ("Basement/SM_VCR", (-0.1, -0.95, 0.0), 0, True), ("Basement/SM_VCR", (-0.1, -0.95, 0.09), 0, False),
            ("Basement/SM_VHS_Stack", (-0.1, -0.95, 0.18), 0, False), ("Basement/SM_VHS_Floor", (-0.7, -0.5, 0), 0, False),
            ("Basement/SM_PC_Tower", (0.0, 0.25, 0), 0, False)):
        a = mesh(path, local_to_world(origin, yaw, local), yaw - lyaw, cb, collision=coll)
        if path.endswith("_Recording"):
            a.set_actor_label("RecordingMonitor")
    tapes = find("ClosedBasement_Tapes")
    if tapes:
        tapes.get_editor_property("static_mesh_component").set_visibility(False)
        for k in range(3):
            mesh("Basement/SM_VHS_Stack", (930 + k * 25, 440, CLOSED_BASEMENT + k * 0.5), 15 * k, cb, collision=False)
        mesh("Props/SM_Box_Open_B", (960, 460, CLOSED_BASEMENT), 0, cb, collision=False)
    mesh("Basement/SM_JunctionBox", (560, 120, CLOSED_BASEMENT + 230), -90, cb, collision=False)
    point_light("Light_RedLamp", local_to_world(origin, yaw, (0.0, 0.45, 1.25)), 500, 500, (255, 40, 30))
    point_light("Light_Screens", local_to_world(origin, yaw, (-0.6, 0.0, 1.1)), 140, 300, (200, 215, 255))

    # Second floor.
    for k, label in enumerate(("BulbRoom_Boxes_A", "BulbRoom_Boxes_B")):
        block = find(label)
        if block:
            x1, x2, y1, y2, z1, z2 = cube_box(block)
            block.get_editor_property("static_mesh_component").set_visibility(False)
            for j in range(3):
                mesh("Props/SM_Box_Closed_A" if j % 2 else "Props/SM_Box_Closed_B", ((x1 + x2) / 2 + 8 * j, (y1 + y2) / 2, z1 + 38 * j), 12 * j - 10, f2, collision=False)
    dress("BulbRoom_Table", "Rooms/SM_Desk_Cabriole", yaw=90, folder=f2)
    mesh("Rooms/SM_TV_Old", (275, -290, F2 + 78), -90, f2, collision=False)
    dress("BulbRoom_Shelf", "Props/SM_Shelving_Metal", yaw=90, folder=f2)
    mesh("Rooms/SM_Flashlight", (230, -270, F2 + 78), 40, f2, collision=False)
    for x, y, yaw_s in ((0 + 11, -420, -90), (0 + 11, -150, -90), (550 - 11, -420, 90), (550 - 11, -150, 90)):
        mesh("Rooms/SM_LampSocket", (x, y, F2 + 200), yaw_s, f2, collision=False)
    # Hallway upstairs: the portrait clue, the blood trail, the police tape.
    painting = find("Hall_Painting")
    if painting:
        painting.get_editor_property("static_mesh_component").set_visibility(False)
    mesh("Rooms/SM_Frame_Portrait", (600, 64, F2 + 170), 180, f2, collision=False, material="Painting_Portrait", slot="M_Painting")
    trail = find("Hall_BloodTrail")
    if trail:
        trail.get_editor_property("static_mesh_component").set_visibility(False)
    for k, x in enumerate((300, 540, 780, 1020)):
        mesh("Rooms/SM_BloodTrail", (x, 25, F2), 4 * (k % 2) - 2, f2, collision=False)
    # Golden apple room: seven paintings on the back and side walls.
    for k, label in enumerate(("Apple_Painting_0", "Apple_Painting_1")):
        block = find(label)
        if block:
            x1, x2, y1, y2, z1, z2 = cube_box(block)
            actors.destroy_actor(block)
            mesh("Rooms/SM_Frame_Gilt_Large" if k else "Rooms/SM_Frame_Gilt_Medium", (1250 - 10, (y1 + y2) / 2, (z1 + z2) / 2), 90, f2,
                 collision=False, material="Painting_Apple%d" % (k + 2) if k else "Painting", slot="M_Painting")
    for k, (x, frame) in enumerate(((760, "SM_Frame_Gilt_Small"), (960, "SM_Frame_Gilt_Medium"), (1140, "SM_Frame_Gilt_Small"))):
        mesh("Rooms/" + frame, (x, -490 + 1, F2 + 160 + 15 * (k % 2)), 0, f2, collision=False, material="Painting_Apple%d" % (k + 4), slot="M_Painting")
    dress("Apple_Wardrobe", "Rooms/SM_Wardrobe_Red", yaw=180, folder=f2)
    dress("Bedroom_Bed", "Rooms/SM_Bed_Single", folder=f2)
    dress("Bedroom_Wardrobe", "Rooms/SM_Wardrobe_Red", yaw=180, folder=f2)
    mesh("Rooms/SM_Nightstand", (540 - 30, 260, F2), 0, f2)
    dress("Kids_Bed", "Rooms/SM_Bed_Single", folder=f2)
    dress("Kids_ToyBox", "Props/SM_Crate_Wood", folder=f2)
    dress("Landing_Dresser", "Attic/SM_Dresser_Attic", yaw=90, folder=f2)
    safe = find("Safe")
    if safe:
        set_look(safe, "Arch_MetalDark")

    # Attic (Attic_Radio).
    station_loc = (HOUSE_DEPTH - 10, -180, ATTIC)
    dress_station = find("Radio_Station")
    if dress_station:
        dress_station.get_editor_property("static_mesh_component").set_visibility(False)
    mesh("Attic/SM_RadioStation", station_loc, 90, at, collision=False)
    sockets_path = os.path.join(PROJECT, "SourceArt", "Models", "Attic", "RadioStation_sockets.json")
    import json
    for s in json.load(open(sockets_path, encoding="utf-8"))["sockets"]:
        a = mesh("Attic/" + s["mesh"], local_to_world(station_loc, 90, s["location"]), 90, at + "/Puzzle", collision=False, roll=-s["rotation"][0])
        a.set_actor_label("Radio_" + s["name"])
    for k, x in enumerate(range(150, 1600, 300)):
        mesh("Attic/SM_Attic_Beam_400", (x, -280, 900), 90, at, collision=False, scale=(1.4, 1, 1))
    for k, (path, loc, yaw_p) in enumerate((("Attic/SM_Cables_Floor", (1350, -250, ATTIC), 180), ("Attic/SM_Transformer_Old", (1250, 180, ATTIC), 0),
                                            ("Attic/SM_Papers_Floor", (1100, -100, ATTIC), 0), ("Attic/SM_Dresser_Attic", (900, 380, ATTIC), 90),
                                            ("Props/SM_Box_Open_A", (1000, -380, ATTIC), 20), ("Props/SM_Box_Closed_A", (800, -360, ATTIC), -10),
                                            ("Props/SM_Crate_Wood", (200, 300, ATTIC), 5))):
        mesh(path, loc, yaw_p, at, collision=path.endswith(("Crate_Wood", "Dresser_Attic")))
    for b in find_prefix("Wardrobe_"):
        if isinstance(b, unreal.StaticMeshActor):
            set_look(b, "Arch_WoodWorn")
    mesh("Hallway/SM_SpiderWeb", (1580, 0, ATTIC + 150), -90, at, collision=False)

    # Lamps for the room lights of the blockout.
    for light in find_prefix("Light_"):
        loc = light.get_actor_location()
        if loc.z > RIDGE - 400 or loc.z < 0:
            continue
        ceiling = F2 - T if loc.z < F2 else ATTIC - T
        mesh("Hallway/SM_CeilingLamp", (loc.x, loc.y, ceiling), 0, "Art/Lamps", collision=False)
    for name in ("Light_FuseBasement", "Light_ClosedBasement"):
        light = find(name)
        if light:
            l = light.get_actor_location()
            mesh("Rooms/SM_LampSocket_Bulb", (l.x, l.y, F1 - T - 1), 0, "Art/Lamps", collision=False, pitch=90)


def dress_outside():
    yard = "Art/Yard"
    # Back yard junk on the blockout cover blocks.
    for label, path, yaw in (("WoodPile", "Yard/SM_Firewood_Pile", 90), ("Barrel_A", "Yard/SM_Barrel_Rust", 0), ("Barrel_B", "Yard/SM_Barrel_Rust", 40),
                             ("Crate_A", "Props/SM_Crate_Wood", 10), ("Crate_B", "Props/SM_Crate_Wood", -20), ("Wheelbarrow", "Yard/SM_Wheelbarrow", 120),
                             ("Crate_UnderPantryWindow", "Props/SM_Crate_Wood", 0)):
        dress(label, path, yaw=yaw, folder=yard)
    ladder = find("FireLadder_Placeholder")
    if ladder:
        x1, x2, y1, y2, z1, z2 = cube_box(ladder)
        ladder.get_editor_property("static_mesh_component").set_visibility(False)
        mesh("Yard/SM_Ladder_Wood", ((x1 + x2) / 2 + 10, (y1 + y2) / 2, 0), 90, yard, collision=False, scale=(1, 1, (z2 - z1) / 300.0), pitch=-6)
    for label, path, yaw in (("Tree_Big", "Outdoor/SM_Tree_Oak_A", 30), ("Tree_Right", "Outdoor/SM_Tree_Oak_B", 200)):
        trunk = find(label + "_Trunk")
        crown = find(label + "_Crown")
        if trunk:
            x1, x2, y1, y2, z1, z2 = cube_box(trunk)
            trunk.get_editor_property("static_mesh_component").set_visibility(False)
            mesh(path, ((x1 + x2) / 2, (y1 + y2) / 2, 0), yaw, yard, collision=False)
        if crown:
            actors.destroy_actor(crown)
    rnd = random.Random(7)
    for k, (path, loc, yaw) in enumerate((("Outdoor/SM_Tree_Dead", (3600, 300, 0), 70), ("Yard/SM_Stump", (2700, 1000, 0), 0),
                                          ("Yard/SM_Hose_Coil", (1750, 300, 0), 0), ("Yard/SM_Planks_Heap", (2500, -500, 0), 30),
                                          ("Yard/SM_Barrel_Rust_Lying", (2750, 650, 0), 80), ("Yard/SM_Shovel", (1700, 450, 0), 10),
                                          ("Yard/SM_Rake", (1900, -700, 0), 100), ("Basement/SM_Puddle_Large", (2300, 200, 1), 0),
                                          ("Basement/SM_Puddle_Large", (-500, 600, 1), 60), ("Basement/SM_Puddle_Small", (2900, -300, 1), 0))):
        mesh(path, loc, yaw, yard, collision=path.endswith(("Stump", "Lying", "Tree_Dead")))
    for k in range(10):
        mesh(rnd.choice(("Outdoor/SM_Bush_A", "Outdoor/SM_Bush_B")), (rnd.uniform(1100, 3300), rnd.choice((-1, 1)) * rnd.uniform(1050, 1250), 0), rnd.uniform(0, 360), yard, collision=False)
    for k in range(160):
        x, y = rnd.uniform(-650, 3350), rnd.uniform(-1280, 1280)
        if -20 < x < HOUSE_DEPTH + 20 and -HALF_WIDTH - 20 < y < HALF_WIDTH + 20:
            continue
        mesh(rnd.choice(("Outdoor/SM_Grass_Tuft_A", "Outdoor/SM_Grass_Tuft_B")), (x, y, 0), rnd.uniform(0, 360), "Art/Grass", collision=False, scale=rnd.uniform(0.8, 1.6))

    # Front yard of the Guest's house: oaks, the van in the side yard (Street_Example).
    street = "Art/Street"
    mesh("Outdoor/SM_Tree_Oak_B", (-350, -1000, 0), 120, street, collision=False)
    mesh("Outdoor/SM_Tree_Oak_A", (-450, 1550, 0), 300, street, collision=False)
    van = mesh("Outdoor/SM_Van", (450, 950, 0), 180, street, label="Van")
    door = mesh("Outdoor/SM_Van_SideDoor", local_to_world((450, 950, 0), 180, (0.85, -0.86, 0.39)), 180, street, label="Van_SideDoor")

    # The street (Street_Example): road along Y, curbs and sidewalks, the player's cottage, mailbox, hedge.
    for k in range(-6, 6):
        y = k * 400
        mesh("Outdoor/SM_Road_400", (-1100, y, 0), 90, street)
        mesh("Outdoor/SM_Curb_400", (-750, y, 0), 90, street)
        mesh("Outdoor/SM_Curb_400", (-1450, y + 400, 0), -90, street)
        mesh("Outdoor/SM_Sidewalk_400", (-732, y, 0), 90, street)
        mesh("Outdoor/SM_Sidewalk_400", (-1468, y + 400, 0), -90, street)
    for name in ("PlayerHouse", "PlayerHouse_Roof"):
        a = find(name)
        if a:
            actors.destroy_actor(a)
    mesh("Yard/SM_PlayerHouse", (-2000, 0, 0), -90, "Art/PlayerHouse", label="PlayerHouse")
    mesh("Outdoor/SM_Mailbox", (-1720, 250, 0), 0, street)
    for k in range(5):
        mesh("Outdoor/SM_Hedge_200", (-1700, -2400 + k * 220, 0), 90, street)
        mesh("Outdoor/SM_Hedge_200", (-1700, 500 + k * 220, 0), 90, street)
    mesh("Outdoor/SM_Tree_Street", (-1650, -900, 0), 0, street, collision=False)
    mesh("Outdoor/SM_Tree_Street", (-1650, 1600, 0), 140, street, collision=False)
    # Warm windows of the player's house and a street lamp glow in the rain.
    point_light("Light_PlayerHouseWindow", (-2050, 0, 180), 2500, 900, (255, 190, 120))
    point_light("Light_StreetGlow", (-1100, 300, 600), 6000, 1800, (190, 200, 255))
    point_light("Light_VanArea", (300, 900, 380), 2500, 900, (170, 185, 230), shadows=True)


def rain():
    """Rain curtains over the outdoor area in 5 m tiles, none over the two houses."""
    folder = "Weather/Rain"
    houses = ((-10, HOUSE_DEPTH + 10, -HALF_WIDTH - 10, HALF_WIDTH + 10), (-2900, -1950, -380, 380))
    count = 0
    for i in range(-7, 8):
        for j in range(-5, 5):
            x, y = i * 500, j * 500
            if any(x < hx2 and x + 500 > hx1 and y < hy2 and y + 500 > hy1 for hx1, hx2, hy1, hy2 in houses):
                continue
            mesh("Outdoor/SM_RainCurtains_1000", (x, y, 0), 0, folder, scale=(0.5, 0.5, 1.0), collision=False)
            count += 1
    unreal.log("Hello Guest: %d rain tiles" % count)


# --- 4./5. Storm and finale (need the C++ classes AHGStorm and AHGFinaleTrigger) ------------------

def hg_class_or_none(name):
    return unreal.load_class(None, "/Script/HelloGuest." + name)


def storm():
    cls = hg_class_or_none("HGStorm")
    if cls is None:
        unreal.log_warning("Hello Guest: HGStorm is not compiled yet, the level has rain but no lightning")
        return
    a = actors.spawn_actor_from_class(cls, unreal.Vector(0, 0, 3000))
    a.set_actor_label("Storm")
    a.set_folder_path("Weather")
    a.set_editor_property("sky_dome", find("SkyDome"))
    a.set_editor_property("thunder_sounds", [unreal.load_asset(ART + "Audio/" + n) for n in ("S_Thunder_Near", "S_Thunder_Mid", "S_Thunder_Far")])
    rain_audio = a.get_editor_property("rain_audio")
    rain_audio.set_editor_property("sound", unreal.load_asset(ART + "Audio/S_RainLoop"))


# (start, seconds on screen, Russian, English)
SUBTITLES = [
    (0.9, 2.8, "Витёк: Анита! Я же просил никого не пускать во время стрима!", "Vitec: Anita! I told you not to let anyone in while I'm streaming!"),
    (4.2, 3.0, "Витёк: Ну ладно, иди покажу кое-что странное.", "Vitec: Okay, fine... come here, I'll show you something weird."),
    (10.6, 3.0, "КАМЕРА 2 · 02:13", "CAMERA 2 · 02:13 AM"),
]
FPS = 30


def finale():
    folder = "Finale"
    settings = unreal.get_default_object(unreal.HGGameplaySettings)
    mesh_yaw = settings.get_editor_property("character_mesh_yaw_offset")
    # Vitec at the console, back to the room (he turns round in A_Vitec_TurnShout).
    # Vitec streams sitting on the office chair in front of the monitors (the desk edge is at X 647,
    # the seated pose puts his hands 46-63 cm in front of the pelvis, over the keyboard).
    vitec_loc = (682, 300, CLOSED_BASEMENT)
    chair = mesh("Basement/SM_OfficeChair", vitec_loc, 0, folder, label="Vitec_Chair")
    vitec = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(*vitec_loc), unreal.Rotator(roll=0, pitch=0, yaw=180))
    vitec.set_actor_label("Vitec")
    vitec.set_folder_path(folder)
    vc = vitec.get_editor_property("skeletal_mesh_component")
    vc.set_skeletal_mesh_asset(unreal.load_asset(ART + "Characters/Vitec/SK_Vitec"))
    anims = {n: unreal.load_asset(ART + "Characters/Vitec/SK_Vitec_Anim_SK_Vitec_A_Vitec_" + n) for n in ("Work", "TurnShout", "CalmTalk", "StandUp", "Beckon", "Idle")}
    vc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    play = unreal.SingleAnimationPlayData()
    play.set_editor_property("anim_to_play", anims["Work"])
    play.set_editor_property("saved_looping", True)
    play.set_editor_property("saved_playing", True)
    vc.set_editor_property("animation_data", play)

    # CCTV camera over the side yard and the render target the recording monitor shows.
    rt_path = SEQ_DIR + "/RT_Recording"
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    rt = unreal.load_asset(rt_path) if unreal.EditorAssetLibrary.does_asset_exist(rt_path) else tools.create_asset("RT_Recording", SEQ_DIR, unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x", 480)
    rt.set_editor_property("size_y", 360)
    unreal.EditorAssetLibrary.save_loaded_asset(rt)
    mi_path = SEQ_DIR + "/MI_ScreenRecording_Live"
    mi = unreal.load_asset(mi_path) if unreal.EditorAssetLibrary.does_asset_exist(mi_path) else tools.create_asset("MI_ScreenRecording_Live", SEQ_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel = unreal.MaterialEditingLibrary
    mel.set_material_instance_parent(mi, unreal.load_asset(MATS + "MI_ScreenRecording"))
    mel.set_material_instance_texture_parameter_value(mi, "BaseColorTex", rt)
    mel.set_material_instance_scalar_parameter_value(mi, "EmissiveStrength", 2.2)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    monitor = find("RecordingMonitor")
    if monitor:
        c = monitor.get_editor_property("static_mesh_component")
        c.set_material(c.get_material_index("M_ScreenRecording"), mi)
    # Over the front yard: the porch on the left, the van's side door facing the camera.
    cam_loc = unreal.Vector(-470, 260, 330)
    target = unreal.Vector(150, 640, 70)
    capture = actors.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, target))
    capture.set_actor_label("CCTV_Camera")
    capture.set_folder_path(folder)
    cc = capture.get_editor_property("capture_component2d")
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("fov_angle", 60.0)
    cc.set_editor_property("capture_every_frame", False)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    pp = cc.get_editor_property("post_process_settings")
    pp.set_editor_property("override_color_saturation", True)
    pp.set_editor_property("color_saturation", unreal.Vector4(0.25, 0.25, 0.25, 1))
    pp.set_editor_property("override_film_grain_intensity", True)
    pp.set_editor_property("film_grain_intensity", 0.8)
    pp.set_editor_property("override_auto_exposure_method", True)
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("override_auto_exposure_bias", True)
    pp.set_editor_property("auto_exposure_bias", 10.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.set_editor_property("post_process_blend_weight", 1.0)

    # The recording: the Guest backs from the porch to the van dragging the neighbour.
    guest_parts = [unreal.load_asset("/Game/Characters/Guest/Guest/SkeletalMeshes/Object_7"), unreal.load_asset("/Game/Characters/Guest/Guest/SkeletalMeshes/Object_9")]
    neighbour_parts = [unreal.load_asset("/Game/Characters/Neighbor/Neighbor/SkeletalMeshes/" + n) for n in ("Object_7", "Object_8", "Object_10", "Object_11", "Object_12", "Object_13")]
    back_anim = unreal.load_asset("/Game/Characters/Guest/Guest/SkeletalMeshes/GuestA_Guest_Calm_Walk_BacksAway")
    limp_anim = unreal.load_asset("/Game/Characters/Neighbor/Neighbor/SkeletalMeshes/NeighborA_Neighbor_Calm_Idle_SK_Neighbor_Body")

    def skeletal(label, sk, loc, rot):
        a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, rot)
        a.set_actor_label(label)
        a.set_folder_path(folder + "/Recording")
        a.get_editor_property("skeletal_mesh_component").set_skeletal_mesh_asset(sk)
        a.set_actor_hidden_in_game(True)
        return a

    # Route round the front-right corner of the house: porch -> corner -> the van's side door.
    route = [(10.4, unreal.Vector(-320, 280, 0)), (15.0, unreal.Vector(-90, 660, 0)), (20.0, unreal.Vector(420, 820, 0))]

    def pose_at(i):
        """Guest rotation and the neighbour's place and rotation on route point i (backing away)."""
        a = route[max(i - 1, 0)][1] if i > 0 else route[0][1]
        b = route[i][1] if i > 0 else route[1][1]
        move = b - a
        facing = math.degrees(math.atan2(move.y, move.x)) + 180.0
        guest_rot = unreal.Rotator(roll=0, pitch=0, yaw=facing + mesh_yaw)
        front = unreal.Vector(math.cos(math.radians(facing)), math.sin(math.radians(facing)), 0)
        lie = unreal.MathLibrary.make_rot_from_zx(front * -1.0 + unreal.Vector(0, 0, 0.35), unreal.Vector(0, 0, 1))
        lie = unreal.MathLibrary.compose_rotators(unreal.Rotator(roll=0, pitch=0, yaw=mesh_yaw), lie)
        return guest_rot, front * 95.0 + unreal.Vector(0, 0, 25), lie

    poses = [pose_at(i) for i in range(len(route))]
    guests = [skeletal("Rec_Guest_%d" % k, sk, route[0][1], poses[0][0]) for k, sk in enumerate(guest_parts)]
    neighbours = [skeletal("Rec_Neighbour_%d" % k, sk, route[0][1] + poses[0][1], poses[0][2]) for k, sk in enumerate(neighbour_parts)]

    # Camera for the cutscene: in front of Vitec, then on the recording monitor.
    def cine(label, loc, look_at, focal=24.0):
        cam = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(*loc), unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*look_at)))
        cam.set_actor_label(label)
        cam.set_folder_path(folder)
        component = cam.get_cine_camera_component()
        component.set_editor_property("current_focal_length", focal)
        focus = component.get_editor_property("focus_settings")
        focus.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
        component.set_editor_property("focus_settings", focus)
        return cam

    cam_vitec = cine("Cam_Vitec", (1020, 250, CLOSED_BASEMENT + 165), (720, 300, CLOSED_BASEMENT + 150))
    cam_close = cine("Cam_Beckon", (930, 330, CLOSED_BASEMENT + 160), (722, 300, CLOSED_BASEMENT + 140), 32.0)
    screen = local_to_world((610, 300, CLOSED_BASEMENT), 180, (-0.15, 0.1, 1.15))
    # Past Vitec's shoulder (he stands right in front of the monitor).
    cam_screen = cine("Cam_Monitor", (screen[0] + 105, screen[1] + 120, screen[2] + 12), screen, 42.0)

    # The level sequence.
    seq_path = SEQ_DIR + "/LS_Act1_Finale"
    if unreal.EditorAssetLibrary.does_asset_exist(seq_path):
        unreal.EditorAssetLibrary.delete_asset(seq_path)
    seq = tools.create_asset("LS_Act1_Finale", SEQ_DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(FPS, 1))

    def frames(seconds):
        """Sections and keys of the scripting API are in display-rate frames."""
        return unreal.FrameNumber(int(round(seconds * FPS)))

    end = 23.0
    seq.set_playback_start(0)
    seq.set_playback_end(int(end * FPS))

    def anim_section(binding, anim, start, stop, loop_length=None):
        track = binding.find_tracks_by_type(unreal.MovieSceneSkeletalAnimationTrack)
        track = track[0] if track else binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
        section = track.add_section()
        section.set_range(frames(start).value, frames(stop).value)
        params = section.get_editor_property("params")
        params.set_editor_property("animation", anim)
        section.set_editor_property("params", params)
        return section

    vb = seq.add_possessable(vitec)
    # Vitec keeps his last pose (turned to the player); everything else is restored when it ends.
    # Seated: swivels round and shouts, calms down; stands up, beckons, turns back and points at the
    # screen, then watches the recording.
    for anim, start, stop in ((anims["TurnShout"], 0.0, 3.6), (anims["CalmTalk"], 3.6, 7.0), (anims["StandUp"], 7.0, 8.0),
                              (anims["Beckon"], 8.0, 11.4), (anims["Idle"], 11.4, end)):
        section = anim_section(vb, anim, start, stop)
        options = section.get_editor_property("eval_options")
        options.set_editor_property("completion_mode", unreal.MovieSceneCompletionMode.KEEP_STATE)
        section.set_editor_property("eval_options", options)

    def transform_keep(binding, keys):
        track = binding.add_track(unreal.MovieScene3DTransformTrack)
        section = track.add_section()
        section.set_range(0, frames(end).value)
        options = section.get_editor_property("eval_options")
        options.set_editor_property("completion_mode", unreal.MovieSceneCompletionMode.KEEP_STATE)
        section.set_editor_property("eval_options", options)
        ch = section.get_all_channels()
        for t, loc, yaw in keys:
            for i, v in enumerate((loc.x, loc.y, loc.z, 0.0, 0.0, yaw)):
                ch[i].add_key(frames(t), v)

    seat = unreal.Vector(*vitec_loc)
    stood = seat + unreal.Vector(40, 0, 0)        # after the turn he faces +X
    transform_keep(vb, [(0.0, seat, 180.0), (7.0, seat, 180.0), (8.0, stood, 180.0)])
    chair_b = seq.add_possessable(chair)
    transform_keep(chair_b, [(0.0, seat, 0.0), (0.25, seat, 0.0), (0.85, seat, 180.0)])

    def visibility(binding, start, stop):
        track = binding.add_track(unreal.MovieSceneVisibilityTrack)
        section = track.add_section()
        section.set_range(0, frames(end).value)
        ch = section.get_all_channels()[0]
        ch.add_key(frames(0.0), False)
        ch.add_key(frames(start), True)
        ch.add_key(frames(stop), False)

    def transform(binding, keys):
        track = binding.add_track(unreal.MovieScene3DTransformTrack)
        section = track.add_section()
        section.set_range(0, frames(end).value)
        ch = section.get_all_channels()
        for t, loc, rot in keys:
            for i, v in enumerate((loc.x, loc.y, loc.z, rot.roll, rot.pitch, rot.yaw)):
                ch[i].add_key(frames(t), v)

    walk_start = route[0][0]
    for g in guests:
        gb = seq.add_possessable(g)
        visibility(gb, walk_start, end)
        anim_section(gb, back_anim, walk_start, end)
        transform(gb, [(t, loc, poses[i][0]) for i, (t, loc) in enumerate(route)] + [(end, route[-1][1], poses[-1][0])])
    for n in neighbours:
        nb = seq.add_possessable(n)
        visibility(nb, walk_start, 21.0)
        anim_section(nb, limp_anim, walk_start, end)
        last = route[-1][1]
        transform(nb, [(t, loc + poses[i][1], poses[i][2]) for i, (t, loc) in enumerate(route)]
                  + [(21.0, last + poses[-1][1] * 0.2 + unreal.Vector(0, 0, 40), poses[-1][2])])
    door = find("Van_SideDoor")
    db = seq.add_possessable(door)
    closed = door.get_actor_location()
    door_rot = door.get_actor_rotation()
    open_pos = unreal.Vector(*local_to_world((closed.x, closed.y, closed.z), 180, (-1.2, 0, 0)))
    transform(db, [(0.0, closed, door_rot), (12.0, closed, door_rot), (13.0, open_pos, door_rot), (21.2, open_pos, door_rot), (22.0, closed, door_rot)])

    cuts = seq.add_track(unreal.MovieSceneCameraCutTrack)
    for cam, start, stop in ((cam_vitec, 0.0, 7.0), (cam_close, 7.0, 10.4), (cam_screen, 10.4, end)):
        cb_ = seq.add_possessable(cam)
        section = cuts.add_section()
        section.set_range(frames(start).value, frames(stop).value)
        section.set_camera_binding_id(seq.get_binding_id(cb_))
    unreal.EditorAssetLibrary.save_loaded_asset(seq)

    seq_actor = actors.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(700, 300, CLOSED_BASEMENT + 100))
    seq_actor.set_actor_label("Finale_Sequence")
    seq_actor.set_folder_path(folder)
    seq_actor.set_sequence(seq)
    ps = seq_actor.get_editor_property("playback_settings")
    ps.set_editor_property("auto_play", False)
    seq_actor.set_editor_property("playback_settings", ps)

    cls = hg_class_or_none("HGFinaleTrigger")
    if cls is None:
        unreal.log_warning("Hello Guest: HGFinaleTrigger is not compiled yet, the finale has no trigger")
        return
    trig = actors.spawn_actor_from_class(cls, unreal.Vector(1050, 290, CLOSED_BASEMENT + 120))
    trig.set_actor_label("FinaleTrigger")
    trig.set_folder_path(folder)
    trig.set_actor_scale3d(unreal.Vector(1.4, 1.4, 0.8))
    trig.set_editor_property("sequence", seq_actor)
    trig.set_editor_property("recording_camera", capture)
    trig.set_editor_property("speaker", vitec)
    trig.set_editor_property("speaker_anim_after", anims["Idle"])
    trig.set_editor_property("speaker_turn_after", 180.0)   # A_Vitec_Idle faces the console
    lines = []
    for t, d, ru, en in SUBTITLES:
        line_ = unreal.HGSubtitleLine()
        line_.set_editor_property("time", t)
        line_.set_editor_property("duration", d)
        line_.set_editor_property("text_en", en)
        line_.set_editor_property("text_ru", ru)
        lines.append(line_)
    trig.set_editor_property("subtitles", lines)


def build():
    B["open_clean_level"]()
    B["build_environment"]()
    B["build_back_yard"]()
    B["build_shell"]()
    B["build_first_floor"]()
    B["build_second_floor"]()
    B["build_attic_and_roof"]()
    B["build_gameplay"]()
    retexture()
    add_linings()
    dress_doors()
    dress_props()
    dress_outside()
    rain()
    storm()
    finale()
    level_editor.save_current_level()
    unreal.log("Hello Guest: Act 1 art level created at " + MAP_PATH)


build()
