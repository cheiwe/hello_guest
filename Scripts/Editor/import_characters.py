"""
Imports the Guest and the Neighbor from SourceArt/Characters/<Name>/<Name>.glb into
/Game/Characters/<Name>/ (skeletal mesh, materials, textures, animations) and assigns the
Guest's mesh and animations in Project Settings > Game > Hello Guest.

Run in the Unreal Editor: Tools > Execute Python Script... > select this file.
Re-running re-imports and overwrites the assets.
"""

import os
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


def import_glb(name, relative_path):
    source = os.path.join(unreal.Paths.project_dir(), relative_path)
    if not os.path.exists(source):
        unreal.log_warning("Hello Guest: %s not found, skipping %s" % (source, name))
        return None

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


def main():
    guest_folder = None
    for name, path in CHARACTERS.items():
        folder = import_glb(name, path)
        if name == "Guest":
            guest_folder = folder

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
