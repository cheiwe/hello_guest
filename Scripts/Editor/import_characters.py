"""
Imports the Guest and the Neighbor from SourceArt/Characters/<Name>/<Name>.glb into
/Game/Characters/<Name>/ (skeletal mesh, materials, textures, animations) and assigns the
Guest's mesh and animations in Project Settings > Game > Hello Guest.

Run in the Unreal Editor: Tools > Execute Python Script... > select this file.
Re-running re-imports and overwrites the assets. Root motion is removed from the animations
(see lock_root_motion).

If the test level /Game/Maps/L_Sandbox is open, a preview of the Neighbor playing his idle
animation is placed in front of his house (only to look at the model; in the game the Neighbor
appears in the intro and the final video).
"""

import json
import os
import struct

import unreal

CHARACTERS = {
    "Guest": "SourceArt/Characters/Guest/Guest.glb",
    "Neighbor": "SourceArt/Characters/Neighbor/Neighbor.glb",
}

# Animation names inside guest_patch_9.glb.
GUEST_ANIMS = {
    "idle": "A_Guest_Idle_Stand",
    "walk": None,  # the model has no calm walk; the run is played slower
    "run": "A_Guest_Run",
    "search": "A_Guest_SearchingPlayer",
    "catch": "A_Guest_CapturePlayer",
}


# The animations come from a game that moves characters with root motion: the root bone
# travels forward (13.8 m per run cycle) and the model drifts away from the capsule, then
# snaps back. The game moves the capsule itself, so root bone translation is frozen before
# import. The source .glb is not modified; a processed copy goes to Saved/HelloGuestImport.
ROOT_BONE_PREFIXES = ("root", "GLTF_created")


def lock_root_motion(source, destination, prefixes=ROOT_BONE_PREFIXES):
    """Copies a .glb, freezing the translation of the root bones in every animation."""
    data = bytearray(open(source, "rb").read())
    json_length = struct.unpack_from("<I", data, 12)[0]
    gltf = json.loads(bytes(data[20:20 + json_length]))
    bin_offset = 20 + json_length + 8

    nodes = gltf["nodes"]
    accessors = gltf["accessors"]
    views = gltf["bufferViews"]
    locked = set()
    for animation in gltf.get("animations", []):
        for channel in animation["channels"]:
            target = channel["target"]
            name = nodes[target["node"]].get("name", "")
            if target["path"] != "translation" or not name.startswith(prefixes):
                continue
            index = animation["samplers"][channel["sampler"]]["output"]
            if index in locked:
                continue
            accessor = accessors[index]
            if accessor.get("componentType") != 5126 or accessor.get("type") != "VEC3" or "sparse" in accessor:
                continue
            view = views[accessor["bufferView"]]
            start = bin_offset + view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
            stride = view.get("byteStride", 12)
            first = struct.unpack_from("<3f", data, start)
            for i in range(1, accessor["count"]):
                struct.pack_into("<3f", data, start + i * stride, *first)
            accessor["min"] = list(first)
            accessor["max"] = list(first)
            locked.add(index)

    # Rewrite the JSON chunk (padded with spaces to a multiple of 4).
    new_json = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    new_json += b" " * ((4 - len(new_json) % 4) % 4)
    rest = data[20 + json_length:]
    out = bytearray(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(new_json) + len(rest)))
    out += struct.pack("<II", len(new_json), 0x4E4F534A) + new_json + rest
    open(destination, "wb").write(out)
    return len(locked)


def import_glb(name, relative_path):
    original = os.path.join(unreal.Paths.project_dir(), relative_path)
    if not os.path.exists(original):
        unreal.log_warning("Hello Guest: %s not found, skipping %s" % (original, name))
        return None

    work_dir = os.path.join(unreal.Paths.project_saved_dir(), "HelloGuestImport")
    os.makedirs(work_dir, exist_ok=True)
    source = os.path.join(work_dir, os.path.basename(original))
    locked = lock_root_motion(original, source)
    unreal.log("Hello Guest: %s - root motion removed from %d animation tracks" % (name, locked))

    destination = "/Game/Characters/" + name
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = destination
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.log("Hello Guest: imported %s -> %s" % (source, destination))
    return destination


def load_assets(folder):
    assets = []
    for path in unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is not None:
            assets.append(asset)
    return assets


def find_anim(anims, wanted):
    if not wanted:
        return None
    # Exact name first, then "contains" (importers sometimes add prefixes or suffixes).
    for anim in anims:
        if anim.get_name() == wanted:
            return anim
    for anim in anims:
        if wanted in anim.get_name():
            return anim
    unreal.log_warning("Hello Guest: animation %s not found" % wanted)
    return None


def material_names(mesh):
    names = []
    for slot in mesh.get_editor_property("materials"):
        names.append(str(slot.get_editor_property("material_slot_name")).lower())
        material = slot.get_editor_property("material_interface")
        if material is not None:
            names.append(material.get_name().lower())
    return names


def pick_body(meshes):
    for mesh in meshes:
        names = material_names(mesh) + [mesh.get_name().lower()]
        if not any("cloak" in n for n in names):
            return mesh
    return meshes[0]


NEIGHBOR_PREVIEW_LABEL = "NeighborPreview"
NEIGHBOR_PREVIEW_LOCATION = unreal.Vector(-300.0, 300.0, 0.0)


def place_neighbor_preview(folder):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None or world.get_name() != "L_Sandbox":
        unreal.log("Hello Guest: open L_Sandbox and run the script again to place the Neighbor preview")
        return

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old = [a for a in actors.get_all_level_actors() if a.get_actor_label().startswith(NEIGHBOR_PREVIEW_LABEL)]
    if old:
        actors.destroy_actors(old)

    assets = load_assets(folder)
    meshes = [a for a in assets if isinstance(a, unreal.SkeletalMesh)]
    anims = [a for a in assets if isinstance(a, unreal.AnimSequence)]
    yaw = unreal.get_default_object(unreal.HGGameplaySettings).get_editor_property("character_mesh_yaw_offset")

    # The Neighbor is split into several meshes (body, head, hair...). Each gets the idle animation
    # made for its own skeleton; they start together, so they stay in sync.
    for index, mesh in enumerate(meshes):
        skeleton = mesh.get_editor_property("skeleton")
        idle = next((a for a in anims if "Calm_Idle_SK" in a.get_name() and a.get_editor_property("skeleton") == skeleton), None)
        if idle is None:
            idle = next((a for a in anims if "Calm_Idle_SK" in a.get_name()), None)
        actor = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, NEIGHBOR_PREVIEW_LOCATION,
                                              unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        actor.set_actor_label("%s_%d" % (NEIGHBOR_PREVIEW_LABEL, index))
        actor.set_folder_path("Characters")
        component = actor.get_editor_property("skeletal_mesh_component")
        component.set_skeletal_mesh_asset(mesh)
        if idle is not None:
            component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            play_data = unreal.SingleAnimationPlayData()
            play_data.set_editor_property("anim_to_play", idle)
            play_data.set_editor_property("saved_looping", True)
            play_data.set_editor_property("saved_playing", True)
            component.set_editor_property("animation_data", play_data)

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.log("Hello Guest: Neighbor preview placed (%d parts)" % len(meshes))


def main():
    guest_folder = None
    for name, path in CHARACTERS.items():
        folder = import_glb(name, path)
        if name == "Guest":
            guest_folder = folder
        if name == "Neighbor" and folder:
            place_neighbor_preview(folder)

    if not guest_folder:
        return

    assets = load_assets(guest_folder)
    meshes = [a for a in assets if isinstance(a, unreal.SkeletalMesh)]
    anims = [a for a in assets if isinstance(a, unreal.AnimSequence)]
    if not meshes:
        unreal.log_error("Hello Guest: no skeletal mesh was imported for the Guest")
        return

    unreal.log("Hello Guest: Guest skeletal meshes: %s" % [m.get_name() for m in meshes])
    unreal.log("Hello Guest: Guest animations (%d): %s" % (len(anims), sorted(a.get_name() for a in anims)))

    # The Guest comes as two skeletal meshes on one skeleton: the body and the cloak.
    # The body is the main mesh; everything else is attached and follows its animation.
    body = pick_body(meshes)
    extras = [m for m in meshes if m != body]
    unreal.log("Hello Guest: body = %s, extra parts = %s" % (body.get_name(), [m.get_name() for m in extras]))

    unreal.HGGameplaySettings.set_guest_assets(
        body,
        extras,
        find_anim(anims, GUEST_ANIMS["idle"]),
        find_anim(anims, GUEST_ANIMS["walk"]),
        find_anim(anims, GUEST_ANIMS["run"]),
        find_anim(anims, GUEST_ANIMS["search"]),
        find_anim(anims, GUEST_ANIMS["catch"]),
    )
    unreal.log("Hello Guest: Guest model assigned. Press Play to see it.")


main()
