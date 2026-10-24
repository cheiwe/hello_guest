"""
Imports the art made in Blender (SourceArt/Models) and the textures (SourceArt/Textures) into Unreal,
builds the master material and one material instance per material slot name (M_<Name> -> MI_<Name>).

Run with the editor open:  py Scripts/Tools/ue_run.py Scripts/Editor/import_art.py
Safe to run again: textures and meshes are reimported in place, instances are updated.
"""

import os

import unreal

PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOURCE_MODELS = os.path.join(PROJECT, "SourceArt", "Models")
SOURCE_TEXTURES = os.path.join(PROJECT, "SourceArt", "Textures")

ART = "/Game/Art"
MATERIALS = ART + "/Materials"
TEXTURES = ART + "/Textures"
MASTER = MATERIALS + "/M_HG_Master"

# Categories of SourceArt/Models to import into /Game/Art/<Category>.
MODEL_CATEGORIES = ["Hallway", "Props", "Exterior", "Study", "Rooms"]

PH = TEXTURES + "/PolyHaven"
ST = TEXTURES + "/Stylized"

# Material slot -> look. tex: PolyHaven id or stylized name; uv: UV scale (UVs are 1 unit per metre,
# so uv = 1 / real-world size of the texture); tint multiplies the colour.
LOOKS = {
    "Wallpaper": dict(tex=ST + "/T_Wallpaper_Rose_D", normal=PH + "/painted_plaster_wall/painted_plaster_wall_nor_dx_2k", uv=1.4, rough=0.85),
    "WoodPanel": dict(tex="dark_wooden_planks", uv=0.5, tint=(1.15, 0.95, 0.8), rough=0.75),
    "WoodDark": dict(tex="oak_wood_planks", uv=0.8, tint=(0.42, 0.3, 0.22), rough=0.6),
    "WoodFloor": dict(tex="brown_planks_09", uv=1.0, tint=(0.62, 0.42, 0.3), rough=0.8),
    "WoodPainted": dict(tex="oak_wood_planks", uv=0.8, tint=(0.22, 0.12, 0.07), rough=0.55),
    "WoodWeathered": dict(tex="brown_planks_09", uv=1.0, tint=(0.85, 0.8, 0.75), rough=0.9),
    "Trim": dict(tex="painted_plaster_wall", uv=1.0, tint=(1.0, 0.96, 0.88), rough=0.6),
    "Plaster": dict(tex="painted_plaster_wall", uv=0.5, tint=(1.0, 0.93, 0.82), rough=0.9),
    "Brass": dict(tint=(0.78, 0.56, 0.22), metallic=1.0, rough=0.35),
    "MetalRust": dict(tex="rust_coarse_01", uv=1.0, rough=0.85),
    "MetalDark": dict(tint=(0.08, 0.08, 0.09), metallic=0.7, rough=0.45),
    "Chain": dict(tex="rust_coarse_01", uv=4.0, tint=(0.75, 0.62, 0.55), metallic=0.4, rough=0.7),
    "PaintRed": dict(tint=(0.75, 0.12, 0.07), rough=0.45),
    "PaintBlue": dict(tint=(0.3, 0.52, 0.72), rough=0.45),
    "PaintYellow": dict(tint=(0.92, 0.7, 0.1), rough=0.45),
    "PaintGreen": dict(tint=(0.28, 0.62, 0.22), rough=0.45),
    "Web": dict(tint=(0.9, 0.9, 0.9), rough=0.9),
    "Fabric": dict(tint=(0.3, 0.28, 0.2), rough=0.95),
    "Rug": dict(tex=ST + "/T_Rug_Runner_D", uv=1.0, rough=0.95),
    "Glass": dict(tint=(0.55, 0.65, 0.66), rough=0.15, emissive=(0.35, 0.33, 0.28), emissive_strength=0.4),
    "LampShade": dict(tint=(1.0, 0.85, 0.6), rough=0.6, emissive=(1.0, 0.75, 0.45), emissive_strength=4.0),
    "Bakelite": dict(tint=(0.13, 0.12, 0.1), rough=0.3),
    "Picture": dict(tex=ST + "/T_Photo_Couple_D", uv=1.0, rough=0.5),
    "Picture_Woman": dict(tex=ST + "/T_Photo_Woman_D", uv=1.0, rough=0.5),
    # Common props (Workshop, Bulb_room, basements, attic).
    "Cardboard": dict(tex=ST + "/T_Cardboard_D", uv=2.0, rough=0.95),
    "Tape": dict(tint=(0.72, 0.6, 0.4), rough=0.4),
    "WoodCrate": dict(tex="brown_planks_09", uv=1.5, tint=(0.95, 0.78, 0.6), rough=0.85),
    "WoodWorn": dict(tex="oak_wood_planks", uv=0.8, tint=(0.7, 0.5, 0.35), rough=0.8),
    "MetalCan": dict(tex="rust_coarse_01", uv=3.0, tint=(1.3, 1.25, 1.2), metallic=0.6, rough=0.6),
    "MetalPainted": dict(tex="rust_coarse_01", uv=0.6, tint=(1.0, 1.15, 1.1), metallic=0.3, rough=0.7),
    "Paint": dict(tint=(0.85, 0.8, 0.7), rough=0.4),
    "Label": dict(tint=(0.8, 0.7, 0.5), rough=0.8),
    # Exterior (Street_Example: dark teal clapboards, dark worn shingles).
    "Siding": dict(tex="blue_painted_planks", uv=1.0, tint=(0.42, 0.78, 0.74), rough=0.85),
    "Shingle": dict(tex="asphalt_03", uv=2.0, tint=(0.95, 0.85, 0.8), rough=0.9),
    "Brick": dict(tex="red_brick_03", uv=1.0, rough=0.9),
    "Concrete": dict(tex="concrete_floor_worn_001", uv=0.5, rough=0.9),
    "Ground": dict(tex="forrest_ground_01", uv=0.3, rough=1.0),
    "Mud": dict(tex="brown_mud_leaves_01", uv=0.3, rough=1.0),
    "Asphalt": dict(tex="asphalt_03", uv=0.5, rough=0.9),
    "ChainLink": dict(tex=ST + "/T_ChainLink_D", uv=1.0, metallic=0.6, rough=0.5, masked=True),
    "ShingleMoss": dict(tex="asphalt_03", uv=2.0, tint=(0.75, 0.9, 0.6), rough=0.95),
    "Moss": dict(tex="forrest_ground_01", uv=2.0, tint=(0.7, 1.0, 0.5), rough=1.0),
    # Study.
    "Marble": dict(tex="painted_plaster_wall", uv=1.5, tint=(1.05, 1.03, 1.0), rough=0.35),
    "MarbleDark": dict(tint=(0.62, 0.6, 0.57), rough=0.4),
    "BookRed": dict(tex="oak_wood_planks", uv=3.0, tint=(0.75, 0.15, 0.1), rough=0.7),
    "BookGreen": dict(tex="oak_wood_planks", uv=3.0, tint=(0.25, 0.45, 0.25), rough=0.7),
    "BookBlue": dict(tex="oak_wood_planks", uv=3.0, tint=(0.25, 0.32, 0.6), rough=0.7),
    "BookBrown": dict(tex="oak_wood_planks", uv=3.0, tint=(0.6, 0.38, 0.2), rough=0.7),
    "BookOchre": dict(tex="oak_wood_planks", uv=3.0, tint=(1.0, 0.78, 0.35), rough=0.7),
    "Globe": dict(tex=ST + "/T_Globe_D", uv=1.0, rough=0.35),
    "Ink": dict(tint=(0.03, 0.02, 0.06), rough=0.1),
    "Paper": dict(tint=(0.88, 0.84, 0.72), rough=0.9),
    "Leather": dict(tex="oak_wood_planks", uv=2.0, tint=(0.55, 0.3, 0.15), rough=0.55),
    "GlassGreen": dict(tint=(0.1, 0.5, 0.2), rough=0.2, emissive=(0.2, 0.9, 0.3), emissive_strength=1.5),
    # Upstairs rooms.
    "Gilt": dict(tint=(0.75, 0.55, 0.2), metallic=0.85, rough=0.35),
    "GiltDark": dict(tint=(0.4, 0.28, 0.1), metallic=0.8, rough=0.45),
    "Painting": dict(tex=ST + "/T_Painting_Apple1_D", uv=1.0, rough=0.6),
    "Painting_Apple2": dict(tex=ST + "/T_Painting_Apple2_D", uv=1.0, rough=0.6),
    "Painting_Apple3": dict(tex=ST + "/T_Painting_Apple3_D", uv=1.0, rough=0.6),
    "Painting_Apple4": dict(tex=ST + "/T_Painting_Apple4_D", uv=1.0, rough=0.6),
    "Painting_Apple5": dict(tex=ST + "/T_Painting_Apple5_D", uv=1.0, rough=0.6),
    "Painting_Apple6": dict(tex=ST + "/T_Painting_Apple6_D", uv=1.0, rough=0.6),
    "Painting_Portrait": dict(tex=ST + "/T_Painting_Portrait_D", uv=1.0, rough=0.6),
    "WoodPaintedRed": dict(tex="oak_wood_planks", uv=0.8, tint=(0.75, 0.3, 0.22), rough=0.7),
    "WoodPaintedRedDark": dict(tex="oak_wood_planks", uv=0.8, tint=(0.55, 0.2, 0.15), rough=0.7),
    "Fabric_Light": dict(tint=(0.8, 0.78, 0.7), rough=0.95),
    "Blanket": dict(tex=ST + "/T_Rug_Runner_D", uv=1.5, tint=(1.1, 0.95, 0.9), rough=0.95),
    "Screen": dict(tint=(0.18, 0.22, 0.2), rough=0.15),
    "Porcelain": dict(tint=(0.9, 0.88, 0.82), rough=0.3),
    "BulbGlass": dict(tint=(0.95, 0.95, 0.9), rough=0.1),
    "CautionTape": dict(tex=ST + "/T_CautionTape_D", uv=1.0, rough=0.5),
    "BloodTrail": dict(tex=ST + "/T_BloodTrail_D", uv=1.0, rough=0.3, masked=True),
    # Characters: the UVs point into the concept sheet itself.
    "Vitec": dict(tex=ST + "/T_Vitec_Sheet_D", uv=1.0, rough=0.75),
}

# Skeletal characters: FBX with the mesh, the skeleton and all animations.
CHARACTERS = [("Characters/Vitec/SK_Vitec.fbx", ART + "/Characters/Vitec")]

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary


# --- Textures --------------------------------------------------------------------------------------

def import_textures():
    tasks = []
    for root, _dirs, files in os.walk(SOURCE_TEXTURES):
        rel = os.path.relpath(root, SOURCE_TEXTURES).replace("\\", "/")
        for name in files:
            if not name.lower().endswith((".png", ".jpg")):
                continue
            task = unreal.AssetImportTask()
            task.filename = os.path.join(root, name)
            task.destination_path = TEXTURES + ("" if rel == "." else "/" + rel)
            task.replace_existing = True
            task.automated = True
            task.save = False
            tasks.append(task)
    asset_tools.import_asset_tasks(tasks)

    for task in tasks:
        for path in task.imported_object_paths:
            tex = unreal.load_asset(path)
            name = tex.get_name().lower()
            if "_nor_" in name:
                tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
                tex.set_editor_property("srgb", False)
            elif "_rough_" in name or "default_linear" in name:
                tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
                tex.set_editor_property("srgb", False)
            eal.save_loaded_asset(tex)
    unreal.log("Hello Guest art: %d textures imported" % len(tasks))


# --- Master material -------------------------------------------------------------------------------

# Bump when the master graph changes: masters are created once per version (a loaded, referenced
# material can be neither deleted nor safely rebuilt in place), instances are re-parented to the new one.
MASTER_VERSION = 2
OLD_MASTERS = ["M_HG_Master", "M_HG_Masked"]


def build_master(name="M_HG_Base", masked=False):
    """Master material. The masked variant (chain-link, webs) cuts holes with the colour texture's alpha."""
    name = "%s_v%d" % (name, MASTER_VERSION)
    path = MATERIALS + "/" + name
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = asset_tools.create_asset(name, MATERIALS, unreal.Material, unreal.MaterialFactoryNew())
    if mat is None:
        raise RuntimeError("Could not create " + path)
    if masked:
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mat.set_editor_property("two_sided", True)

    def expr(cls, x, y):
        return mel.create_material_expression(mat, cls, x, y)

    coord = expr(unreal.MaterialExpressionTextureCoordinate, -1400, 0)
    uv_scale = expr(unreal.MaterialExpressionScalarParameter, -1400, 120)
    uv_scale.set_editor_property("parameter_name", "UVScale")
    uv_scale.set_editor_property("default_value", 1.0)
    uv = expr(unreal.MaterialExpressionMultiply, -1150, 40)
    mel.connect_material_expressions(coord, "", uv, "A")
    mel.connect_material_expressions(uv_scale, "", uv, "B")

    def sampler(name, x, y, sampler_type, default):
        s = expr(unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        s.set_editor_property("parameter_name", name)
        s.set_editor_property("sampler_type", sampler_type)
        s.set_editor_property("texture", unreal.load_asset(default))
        mel.connect_material_expressions(uv, "", s, "UVs")
        return s

    base_tex = sampler("BaseColorTex", -900, -300, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, "/Engine/EngineResources/WhiteSquareTexture")
    normal_tex = sampler("NormalTex", -900, 0, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, "/Engine/EngineMaterials/DefaultNormal")
    rough_tex = sampler("RoughnessTex", -900, 300, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, TEXTURES + "/Stylized/T_Default_Linear")

    tint = expr(unreal.MaterialExpressionVectorParameter, -600, -450)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    base = expr(unreal.MaterialExpressionMultiply, -350, -320)
    mel.connect_material_expressions(base_tex, "RGB", base, "A")
    mel.connect_material_expressions(tint, "RGB", base, "B")
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    if masked:
        mel.connect_material_property(base_tex, "A", unreal.MaterialProperty.MP_OPACITY_MASK)

    mel.connect_material_property(normal_tex, "RGB", unreal.MaterialProperty.MP_NORMAL)

    rough_scale = expr(unreal.MaterialExpressionScalarParameter, -600, 420)
    rough_scale.set_editor_property("parameter_name", "Roughness")
    rough_scale.set_editor_property("default_value", 0.7)
    rough = expr(unreal.MaterialExpressionMultiply, -350, 330)
    mel.connect_material_expressions(rough_tex, "R", rough, "A")
    mel.connect_material_expressions(rough_scale, "", rough, "B")
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    metallic = expr(unreal.MaterialExpressionScalarParameter, -350, 150)
    metallic.set_editor_property("parameter_name", "Metallic")
    metallic.set_editor_property("default_value", 0.0)
    mel.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

    emissive_color = expr(unreal.MaterialExpressionVectorParameter, -600, 600)
    emissive_color.set_editor_property("parameter_name", "EmissiveColor")
    emissive_color.set_editor_property("default_value", unreal.LinearColor(0, 0, 0, 1))
    emissive_strength = expr(unreal.MaterialExpressionScalarParameter, -600, 760)
    emissive_strength.set_editor_property("parameter_name", "EmissiveStrength")
    emissive_strength.set_editor_property("default_value", 0.0)
    emissive = expr(unreal.MaterialExpressionMultiply, -350, 650)
    mel.connect_material_expressions(emissive_color, "RGB", emissive, "A")
    mel.connect_material_expressions(emissive_strength, "", emissive, "B")
    mel.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    return mat


def polyhaven(asset_id, kind):
    return "%s/%s/%s_%s_2k" % (PH, asset_id, asset_id, kind)


def build_instances(master, masked_master):
    for name, look in LOOKS.items():
        path = MATERIALS + "/MI_" + name
        mi = unreal.load_asset(path) if eal.does_asset_exist(path) else asset_tools.create_asset(
            "MI_" + name, MATERIALS, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, masked_master if look.get("masked") else master)
        mel.clear_all_material_instance_parameters(mi)

        tex = look.get("tex")
        if tex:
            if tex.startswith("/"):
                mel.set_material_instance_texture_parameter_value(mi, "BaseColorTex", unreal.load_asset(tex))
            else:
                mel.set_material_instance_texture_parameter_value(mi, "BaseColorTex", unreal.load_asset(polyhaven(tex, "diff")))
                mel.set_material_instance_texture_parameter_value(mi, "NormalTex", unreal.load_asset(polyhaven(tex, "nor_dx")))
                mel.set_material_instance_texture_parameter_value(mi, "RoughnessTex", unreal.load_asset(polyhaven(tex, "rough")))
        if look.get("normal"):
            mel.set_material_instance_texture_parameter_value(mi, "NormalTex", unreal.load_asset(look["normal"]))
        mel.set_material_instance_scalar_parameter_value(mi, "UVScale", look.get("uv", 1.0))
        mel.set_material_instance_scalar_parameter_value(mi, "Roughness", look.get("rough", 0.7))
        mel.set_material_instance_scalar_parameter_value(mi, "Metallic", look.get("metallic", 0.0))
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*look.get("tint", (1, 1, 1)), 1))
        if look.get("emissive"):
            mel.set_material_instance_vector_parameter_value(mi, "EmissiveColor", unreal.LinearColor(*look["emissive"], 1))
            mel.set_material_instance_scalar_parameter_value(mi, "EmissiveStrength", look.get("emissive_strength", 1.0))
        eal.save_loaded_asset(mi)
    unreal.log("Hello Guest art: %d material instances" % len(LOOKS))


# --- Meshes ----------------------------------------------------------------------------------------

def fbx_options():
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_animations", False)
    data = options.static_mesh_import_data
    # Blender works in metres: convert to centimetres on import.
    data.set_editor_property("convert_scene_unit", True)
    data.set_editor_property("combine_meshes", True)
    data.set_editor_property("auto_generate_collision", False)
    data.set_editor_property("generate_lightmap_u_vs", True)
    data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    return options


def import_meshes():
    # The legacy FBX importer honours FbxImportUI (Interchange would create materials from the FBX).
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX false")
    imported = []
    for category in MODEL_CATEGORIES:
        folder = os.path.join(SOURCE_MODELS, category)
        tasks = []
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith(".fbx") or "_raw" in name.lower():
                continue
            task = unreal.AssetImportTask()
            task.filename = os.path.join(folder, name)
            task.destination_path = "%s/%s" % (ART, category)
            task.destination_name = os.path.splitext(name)[0]
            task.replace_existing = True
            task.automated = True
            task.save = False
            task.options = fbx_options()
            tasks.append(task)
        asset_tools.import_asset_tasks(tasks)
        for task in tasks:
            imported += list(task.imported_object_paths)

    for path in imported:
        mesh = unreal.load_asset(path)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        # Exact collision: the player walks on and against these surfaces, the navmesh uses them too.
        body = mesh.get_editor_property("body_setup")
        if body:
            body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        for index, slot in enumerate(mesh.static_materials):
            slot_name = str(slot.material_slot_name)
            look = slot_name[2:] if slot_name.startswith("M_") else slot_name
            mi_path = MATERIALS + "/MI_" + look
            if eal.does_asset_exist(mi_path):
                mesh.set_material(index, unreal.load_asset(mi_path))
            else:
                unreal.log_warning("Hello Guest art: no material instance for slot %s of %s" % (slot_name, path))
        eal.save_loaded_asset(mesh)
    unreal.log("Hello Guest art: %d meshes imported" % len(imported))


def import_characters():
    """Skeletal mesh + skeleton + animation sequences; material slots get MI_<slot> like the props."""
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX false")
    for rel, dest in CHARACTERS:
        options = unreal.FbxImportUI()
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_as_skeletal", True)
        options.set_editor_property("import_animations", True)
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        options.set_editor_property("create_physics_asset", True)
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        options.skeletal_mesh_import_data.set_editor_property("convert_scene_unit", True)
        options.skeletal_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        options.anim_sequence_import_data.set_editor_property("convert_scene_unit", True)
        options.anim_sequence_import_data.set_editor_property("import_bone_tracks", True)

        task = unreal.AssetImportTask()
        task.filename = os.path.join(SOURCE_MODELS, rel)
        task.destination_path = dest
        task.replace_existing = True
        task.automated = True
        task.save = False
        task.options = options
        asset_tools.import_asset_tasks([task])

        for path in task.imported_object_paths:
            asset = unreal.load_asset(path)
            if isinstance(asset, unreal.SkeletalMesh):
                # The array holds copies of the structs: build new ones and set the whole array.
                materials = []
                for slot in asset.get_editor_property("materials"):
                    look = str(slot.material_slot_name)
                    look = look[2:] if look.startswith("M_") else look
                    mi_path = MATERIALS + "/MI_" + look
                    materials.append(unreal.SkeletalMaterial(
                        material_interface=unreal.load_asset(mi_path) if eal.does_asset_exist(mi_path) else slot.material_interface,
                        material_slot_name=slot.material_slot_name))
                asset.set_editor_property("materials", materials)
            eal.save_loaded_asset(asset)
        # The task lists only the mesh; the skeleton, physics asset and animations need saving too.
        eal.save_directory(dest, only_if_is_dirty=True)
        unreal.log("Hello Guest art: character %s -> %s" % (rel, [str(p) for p in task.imported_object_paths]))


def main():
    # Work from a level that does not use the art, so materials and meshes can be replaced.
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    previous = level_editor.get_current_level().get_outermost().get_name()
    level_editor.load_level("/Game/Maps/L_Sandbox")

    import_textures()
    master = build_master()
    masked_master = build_master("M_HG_BaseMasked", masked=True)
    build_instances(master, masked_master)
    # Masters of older versions are unreferenced now.
    for asset in eal.list_assets(MATERIALS, recursive=False):
        short = asset.split("/")[-1].split(".")[0]
        if (short in OLD_MASTERS or short.startswith(("M_HG_Base_v", "M_HG_BaseMasked_v"))) and short not in (master.get_name(), masked_master.get_name()):
            if not eal.delete_asset(asset.split(".")[0]):
                unreal.log_warning("Hello Guest art: old master %s is still referenced" % short)
    import_meshes()
    import_characters()
    if previous != "/Game/Maps/L_Sandbox":
        level_editor.load_level(previous)


main()
