"""
Vitec rig and animations. Run after vitec_character.py (it opens Vitec_Textured.blend itself).

Skeleton: Unreal-mannequin-like names, joints placed from measurements of the mesh (facing +X, left = +Y,
1.80 m). Weights: Blender automatic weights. Animations are keyframed from pose tables (see ANIMS):
rotations are axis-angle in the armature rest frame, applied in each bone's local frame, so a child's
rotation is relative to its parent (bend the elbow after raising the arm).

Axes in the rest frame: lean forward = +Y, turn left = +Z, left arm down = -X (right arm down = +X),
arm forward = -Y, forearm forward (elbow flex) = -Y.
"""

import importlib
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, r"E:\Project\Unreal Projects\Hello Guest\hello_guest\Scripts\Blender")
import hg_blender as hg  # noqa: E402
importlib.reload(hg)

FOLDER = os.path.join(hg.MODELS_DIR, "Characters", "Vitec")
FPS = 30

# Bone: (head, tail, parent). Left side; the right side is mirrored in Y.
BONES = {
    "root": ((0, 0, 0), (0, 0.2, 0), None),
    "pelvis": ((0, 0, 0.98), (0, 0, 1.06), "root"),
    "spine_01": ((0, 0, 1.06), (0, 0, 1.18), "pelvis"),
    "spine_02": ((0, 0, 1.18), (0, 0, 1.32), "spine_01"),
    "spine_03": ((0, 0, 1.32), (0.005, 0, 1.46), "spine_02"),
    "neck_01": ((0.005, 0, 1.46), (0.015, 0, 1.56), "spine_03"),
    "head": ((0.015, 0, 1.56), (0.02, 0, 1.8), "neck_01"),
    "clavicle_l": ((0.0, 0.04, 1.43), (0.0, 0.17, 1.43), "spine_03"),
    "upperarm_l": ((0.0, 0.19, 1.42), (-0.03, 0.36, 1.17), "clavicle_l"),
    "lowerarm_l": ((-0.03, 0.36, 1.17), (0.02, 0.46, 0.94), "upperarm_l"),
    "hand_l": ((0.02, 0.46, 0.94), (0.05, 0.51, 0.78), "lowerarm_l"),
    "thigh_l": ((0.0, 0.1, 0.95), (0.02, 0.11, 0.52), "pelvis"),
    "calf_l": ((0.02, 0.11, 0.52), (-0.02, 0.12, 0.12), "thigh_l"),
    "foot_l": ((-0.02, 0.12, 0.12), (0.1, 0.13, 0.03), "calf_l"),
    "ball_l": ((0.1, 0.13, 0.03), (0.17, 0.13, 0.03), "foot_l"),
}


def mirrored():
    out = {}
    for name, (head, tail, parent) in BONES.items():
        out[name] = (head, tail, parent)
        if name.endswith("_l"):
            r = name[:-2] + "_r"
            out[r] = ((head[0], -head[1], head[2]), (tail[0], -tail[1], tail[2]), parent[:-2] + "_r" if parent.endswith("_l") else parent)
    return out


def build_armature(mesh):
    bones = mirrored()
    arm_data = bpy.data.armatures.new("SK_Vitec_Skeleton")
    arm = bpy.data.objects.new("SK_Vitec", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (head, tail, parent) in bones.items():
        b = arm_data.edit_bones.new(name)
        b.head = head
        b.tail = tail
        # Roll so that every bone's local X points to the character's left (+Y) where possible.
        b.align_roll(Vector((0, 0, 1)) if abs(Vector(tail).z - Vector(head).z) < 0.05 else Vector((-1, 0, 0)))
    for name, (head, tail, parent) in bones.items():
        if parent:
            arm_data.edit_bones[name].parent = arm_data.edit_bones[parent]
            arm_data.edit_bones[name].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")

    # Skin with automatic weights.
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    unweighted = sum(1 for v in mesh.data.vertices if not any(g.weight > 0.01 for g in v.groups))
    print("armature built, vertices without weights:", unweighted, "of", len(mesh.data.vertices))
    return arm


def pose_quat(arm, bone_name, axis, degrees):
    """Rotation about an armature-rest-frame axis, expressed in the bone's local frame."""
    rest = arm.data.bones[bone_name].matrix_local.to_3x3()
    world = Quaternion(Vector(axis), math.radians(degrees))
    return (rest.inverted() @ world.to_matrix() @ rest).to_quaternion()


def apply_pose(arm, pose):
    """pose: {bone: [(axis, degrees), ...]} - rotations composed in order. Unlisted bones go to rest.
    "pelvis_offset": [(x, y, z), ...] moves the pelvis in the armature rest frame (metres, summed)."""
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        q = Quaternion()
        for axis, deg in pose.get(pb.name, []):
            q = pose_quat(arm, pb.name, axis, deg) @ q
        pb.rotation_quaternion = q
        pb.location = (0, 0, 0)
    offset = Vector((0, 0, 0))
    for o in pose.get("pelvis_offset", []):
        offset += Vector(o)
    pelvis = arm.pose.bones["pelvis"]
    pelvis.location = arm.data.bones["pelvis"].matrix_local.to_3x3().inverted() @ offset


def test_pose(arm):
    """Arms down, slight lean, head turn: to check the skinning by eye."""
    apply_pose(arm, {
        "upperarm_l": [((1, 0, 0), -45)], "upperarm_r": [((1, 0, 0), 45)],
        "lowerarm_l": [((0, 1, 0), -40)], "lowerarm_r": [((0, 1, 0), -40)],
        "spine_02": [((0, 1, 0), 10)], "head": [((0, 0, 1), 25)],
        "thigh_l": [((0, 1, 0), -30)], "calf_l": [((0, 1, 0), 50)],
    })


# --- Poses (rest = the A-pose of the mesh) -------------------------------------------------------

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def merge(*poses):
    out = {}
    for p in poses:
        for bone, rots in p.items():
            out[bone] = out.get(bone, []) + list(rots)
    return out


# The mesh's A-pose arms are only ~29 degrees off vertical: lowering them more than that pushes the hands
# into the thighs. 16 degrees down and a little forward leaves the hands hanging beside the trouser pockets.
ARMS_RELAXED = {"upperarm_l": [(X, -16), (Y, -6)], "upperarm_r": [(X, 16), (Y, -6)], "lowerarm_l": [(Y, -10)], "lowerarm_r": [(Y, -10)]}

WORK = merge({
    "spine_01": [(Y, 8)], "spine_02": [(Y, 8)], "neck_01": [(Y, 4)], "head": [(Y, 10)],
    "upperarm_l": [(X, -30), (Y, -45)], "upperarm_r": [(X, 30), (Y, -45)],
    "lowerarm_l": [(Y, -55)], "lowerarm_r": [(Y, -55)],
    "thigh_l": [(Y, -4)], "thigh_r": [(Y, -4)], "calf_l": [(Y, 6)], "calf_r": [(Y, 6)],
})


# Sitting on the office chair (he streams from the console): pelvis down onto the seat, thighs
# forward and level, shins down. The pelvis stays above the root, so a root turn swivels him in place
# like the chair under him.
SIT = {
    "pelvis_offset": [(0.0, 0.0, -0.38)],
    "thigh_l": [(Y, -79)], "thigh_r": [(Y, -79)], "calf_l": [(Y, 84)], "calf_r": [(Y, 84)],
    "foot_l": [(Y, -6)], "foot_r": [(Y, -6)],
}

# Seated, the shoulders are 38 cm lower than standing: the same forearm angle puts the hands on a
# keyboard at desk height (76 cm).
WORK_SEATED = merge(WORK, SIT, {"upperarm_l": [(Y, -6)], "upperarm_r": [(Y, -6)], "lowerarm_l": [(Y, -4)], "lowerarm_r": [(Y, -4)]})

# Seated with the hands resting on the thighs (no arms hanging into the legs).
LAP = {"upperarm_l": [(X, -24), (Y, -20)], "upperarm_r": [(X, 24), (Y, -20)], "lowerarm_l": [(Y, -42)], "lowerarm_r": [(Y, -42)], "hand_l": [(Y, 12)], "hand_r": [(Y, 12)]}


def typing(t, seated=True):
    """Small alternating hand motion on the keyboard."""
    s = math.sin(t * 2 * math.pi * 3)
    return merge(WORK_SEATED if seated else WORK, {"lowerarm_l": [(Y, 4 * s)], "lowerarm_r": [(Y, -4 * s)], "hand_l": [(Y, 6 * s)], "hand_r": [(Y, -6 * s)]})


SHOUT_A = merge({
    # Leaning in, chin up, forearms up and out: "what are you doing here?!"
    "spine_01": [(Y, 10)], "spine_02": [(Y, 8)], "spine_03": [(Y, 4)], "neck_01": [(Y, 12)], "head": [(Y, -16)],
    "upperarm_l": [(X, 12), (Y, -35)], "upperarm_r": [(X, -12), (Y, -35)],
    "lowerarm_l": [(Y, -62)], "lowerarm_r": [(Y, -62)],
    "hand_l": [(X, 20)], "hand_r": [(X, -20)],
    "clavicle_l": [(X, 8)], "clavicle_r": [(X, -8)],
})

SHOUT_B = merge({
    # Punch on the stressed words: lunge forward, arms thrust down and forward, head jut.
    "spine_01": [(Y, 16)], "spine_02": [(Y, 12)], "spine_03": [(Y, 6)], "neck_01": [(Y, 16)], "head": [(Y, -22)],
    "upperarm_l": [(X, -5), (Y, -55)], "upperarm_r": [(X, 5), (Y, -55)],
    "lowerarm_l": [(Y, -28)], "lowerarm_r": [(Y, -28)],
    "hand_l": [(Y, -15)], "hand_r": [(Y, -15)],
    "clavicle_l": [(X, 12)], "clavicle_r": [(X, -12)],
    "thigh_l": [(Y, -6)], "calf_l": [(Y, 8)],
})

CALM_RUB = merge(ARMS_RELAXED, {
    # Shoulders drop, head tilts, the right hand rubs the back of the neck.
    "spine_02": [(Y, -3)], "neck_01": [(Y, 6)], "head": [(X, -10), (Y, 6)],
    "clavicle_l": [(X, -5)], "clavicle_r": [(X, 5)],
    "upperarm_r": [(X, -100), (Y, -40)], "lowerarm_r": [(Y, -128)], "hand_r": [(Y, -20)],
})

CALM_SHRUG = merge(ARMS_RELAXED, {
    "spine_02": [(Y, -2)], "head": [(X, 8), (Y, 4)],
    "clavicle_l": [(X, 10)], "clavicle_r": [(X, -10)],
    "upperarm_l": [(Y, -25)], "upperarm_r": [(Y, -25)], "lowerarm_l": [(Y, -45)], "lowerarm_r": [(Y, -45)],
    "hand_l": [(X, 25)], "hand_r": [(X, -25)],
})

# Gestures of the right arm are set from the A-pose, with only the left arm relaxed, so the rotations do
# not stack on top of the relaxed right arm.
LEFT_RELAXED = {k: v for k, v in ARMS_RELAXED.items() if k.endswith("_l")}

BECKON_OUT = merge(LEFT_RELAXED, {
    "head": [(Y, 6)],
    "upperarm_r": [(X, 8), (Y, -62)], "lowerarm_r": [(Y, -18)], "hand_r": [(Y, 10)],
})

BECKON_IN = merge(BECKON_OUT, {"lowerarm_r": [(Y, -70)], "hand_r": [(Y, -35)], "head": [(Y, 8)]})

POINT_SCREEN = merge(LEFT_RELAXED, {
    "spine_01": [(Y, 5)], "head": [(Y, 8)],
    "upperarm_r": [(X, 12), (Y, -70)], "lowerarm_r": [(Y, -4)], "hand_r": [(Y, 5)],
})


def turn(degrees):
    return {"root": [(Z, degrees)]}


def anim_work():
    return [(t / 10.0, typing(t / 10.0)) for t in range(0, 41, 2)]


def anim_turn_shout():
    """At the console with his back to the player -> swivels round on the chair (head first) -> shouts the
    line, about 3.6 s. Seated all the way."""
    keys = [(0.0, merge(typing(0.0), turn(0)))]
    keys.append((0.25, merge(WORK_SEATED, turn(0), {"head": [(Z, 45)], "neck_01": [(Z, 20)]})))
    keys.append((0.55, merge(SIT, LAP, turn(110), {"spine_02": [(Z, 25)], "head": [(Z, 20)]})))
    keys.append((0.85, merge(SIT, SHOUT_A, turn(180))))
    beats = [1.15, 1.45, 1.85, 2.2, 2.6, 3.0]
    for i, t in enumerate(beats):
        keys.append((t, merge(SIT, SHOUT_B if i % 2 == 0 else SHOUT_A, turn(180))))
    keys.append((3.6, merge(SIT, SHOUT_A, turn(180))))
    return keys


def anim_calm_talk():
    """Calms down in the chair: rubs his neck, shrugs, "well, all right...", about 3.4 s."""
    lap_l = {k: v for k, v in LAP.items() if k.endswith("_l")}
    return [
        (0.0, merge(SIT, SHOUT_A, turn(180))),
        (0.5, merge(SIT, LAP, turn(180), {"spine_02": [(Y, -3)]})),
        (1.0, merge(SIT, CALM_RUB_SEATED(lap_l), turn(180))),
        (1.4, merge(SIT, CALM_RUB_SEATED(lap_l), turn(180), {"hand_r": [(Y, 15)]})),
        (1.8, merge(SIT, CALM_RUB_SEATED(lap_l), turn(180))),
        (2.4, merge(SIT, CALM_SHRUG, turn(180))),
        (3.0, merge(SIT, LAP, turn(180), {"head": [(Y, 5)]})),
        (3.4, merge(SIT, LAP, turn(180))),
    ]


def CALM_RUB_SEATED(lap_l):
    """The neck rub with the free left hand on the lap instead of hanging beside the leg."""
    rub = {k: v for k, v in CALM_RUB.items() if not k.endswith("_l")}
    return merge(rub, lap_l)


def anim_stand_up():
    """Gets out of the chair, about 1 s: leans forward over the feet, pushes up, straightens."""
    half = {"pelvis_offset": [(0.0, 0.0, -0.2)], "thigh_l": [(Y, -45)], "thigh_r": [(Y, -45)], "calf_l": [(Y, 55)], "calf_r": [(Y, 55)]}
    return [
        (0.0, merge(SIT, LAP, turn(180))),
        (0.35, merge(SIT, LAP, turn(180), {"spine_01": [(Y, 25)], "spine_02": [(Y, 10)]})),
        # Pushes off the knees: the hands stay on them until the legs are almost straight.
        (0.7, merge(half, LAP, turn(180), {"spine_01": [(Y, 20)], "spine_02": [(Y, 8)], "lowerarm_l": [(Y, -12)], "lowerarm_r": [(Y, -12)]})),
        (0.85, merge({"pelvis_offset": [(0.0, 0.0, -0.06)], "thigh_l": [(Y, -12)], "thigh_r": [(Y, -12)], "calf_l": [(Y, 14)], "calf_r": [(Y, 14)]},
                     LAP, turn(180), {"spine_01": [(Y, 8)]})),
        (1.0, merge(ARMS_RELAXED, turn(180))),
    ]


def anim_beckon():
    """"Come, I'll show you something strange": waves the player over, turns back, points at the screen."""
    return [
        (0.0, merge(ARMS_RELAXED, turn(180))),
        (0.4, merge(BECKON_OUT, turn(180))),
        (0.7, merge(BECKON_IN, turn(180))),
        (1.0, merge(BECKON_OUT, turn(180))),
        (1.3, merge(BECKON_IN, turn(180))),
        (1.7, merge(ARMS_RELAXED, turn(120), {"head": [(Z, -30)]})),
        (2.2, merge(POINT_SCREEN, turn(15))),
        (2.6, merge(POINT_SCREEN, turn(0))),
        (3.4, merge(POINT_SCREEN, turn(0))),
    ]


def anim_idle():
    keys = []
    for i in range(9):
        t = i * 0.5
        b = math.sin(t / 4.0 * 2 * math.pi)
        keys.append((t, merge(ARMS_RELAXED, {"spine_02": [(Y, 1.5 * b)], "spine_03": [(Y, 1.0 * b)], "head": [(Z, 4 * math.sin(t / 4.0 * math.pi))]})))
    return keys


ANIMS = {
    "A_Vitec_Work": anim_work,
    "A_Vitec_TurnShout": anim_turn_shout,
    "A_Vitec_CalmTalk": anim_calm_talk,
    "A_Vitec_StandUp": anim_stand_up,
    "A_Vitec_Beckon": anim_beckon,
    "A_Vitec_Idle": anim_idle,
}


def bake_actions(arm):
    """One Blender action per entry of ANIMS, keyed at every pose of its table."""
    scene = bpy.context.scene
    scene.render.fps = FPS
    if arm.animation_data is None:
        arm.animation_data_create()
    actions = []
    for name, maker in ANIMS.items():
        old = bpy.data.actions.get(name)
        if old:
            bpy.data.actions.remove(old)
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        arm.animation_data.action = action
        keys = maker()
        for t, pose in keys:
            apply_pose(arm, pose)
            frame = 1 + round(t * FPS)
            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=frame)
            arm.pose.bones["pelvis"].keyframe_insert("location", frame=frame)
        action.frame_range = (1, 1 + round(keys[-1][0] * FPS))
        actions.append(action)
    arm.animation_data.action = None
    apply_pose(arm, {})
    print("baked actions:", [(a.name, tuple(a.frame_range)) for a in actions])
    return actions


def export_character(arm, mesh):
    """Skeletal mesh + every action in one FBX (Unreal imports the actions as animation sequences)."""
    path = os.path.join(FOLDER, "SK_Vitec.fbx")
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="X",
        axis_up="Z",
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        armature_nodetype="NULL",
        bake_anim=True,
        bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
    )
    print("exported", path)
    return path


# Hands only: sleeves rest against the sides of the hoodie when the arms hang, which is normal contact.
LIMB_GROUPS = {"hand_l", "hand_r"}
BODY_GROUPS = {"pelvis", "spine_01", "spine_02", "spine_03", "thigh_l", "thigh_r", "calf_l", "calf_r", "head", "neck_01"}


def check_intersections(arm, mesh, step=3, threshold=0.015):
    """
    Plays every action and measures, for each sampled frame, how close the hand/forearm vertices come
    to the torso, head and leg vertices. Distances under the threshold mean the hand is touching or
    inside the body. Returns {action: [(frame, min_distance_cm, count), ...]} for the bad frames.
    """
    from mathutils.kdtree import KDTree

    names = {g.index: g.name for g in mesh.vertex_groups}
    dominant = []
    for v in mesh.data.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        dominant.append(names.get(best.group) if best else None)
    limb_ids = [i for i, n in enumerate(dominant) if n in LIMB_GROUPS]
    body_ids = [i for i, n in enumerate(dominant) if n in BODY_GROUPS]

    depsgraph = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    report = {}
    for action in bpy.data.actions:
        if not action.name.startswith("A_Vitec"):
            continue
        arm.animation_data.action = action
        bad = []
        start, end = int(action.frame_range[0]), int(action.frame_range[1])
        for frame in range(start, end + 1, step):
            scene.frame_set(frame)
            evaluated = mesh.evaluated_get(depsgraph)
            co = [v.co.copy() for v in evaluated.data.vertices]
            tree = KDTree(len(body_ids))
            for k, i in enumerate(body_ids):
                tree.insert(co[i], k)
            tree.balance()
            close = [tree.find(co[i])[2] for i in limb_ids]
            hits = [d for d in close if d < threshold]
            if hits:
                bad.append((frame, round(min(hits) * 100, 1), len(hits)))
        report[action.name] = bad
    arm.animation_data.action = None
    return report


def build_rig():
    # Works on the textured mesh in the open scene (run vitec_character.py first in the same session;
    # opening the .blend from a script loses the UI context that mode switching needs).
    for obj in list(bpy.data.objects):
        if obj.type == "ARMATURE":
            bpy.data.objects.remove(obj)
    mesh = bpy.data.objects["SK_Vitec_Mesh"]
    mesh.parent = None
    for mod in list(mesh.modifiers):
        mesh.modifiers.remove(mod)
    mesh.vertex_groups.clear()
    arm = build_armature(mesh)
    bake_actions(arm)
    hg.save_blend(os.path.join(FOLDER, "Vitec_Rigged.blend"))
    export_character(arm, mesh)
    return arm


def rebake():
    """New animations on the existing rig and weights: appends SK_Vitec and its mesh from
    Vitec_Rigged.blend into the open scene, bakes ANIMS, saves and exports."""
    import shutil
    import tempfile
    path = os.path.join(FOLDER, "Vitec_Rigged.blend")
    # Load from a copy: Blender cannot append from the file that is open (or about to be saved over).
    copy = os.path.join(tempfile.gettempdir(), "Vitec_Rigged_src.blend")
    shutil.copyfile(path, copy)
    hg.reset_scene()
    for block in (bpy.data.armatures, bpy.data.actions):
        for item in list(block):
            if item.users == 0 or block is bpy.data.actions:
                block.remove(item)
    with bpy.data.libraries.load(copy) as (src, dst):
        dst.objects = [n for n in src.objects if n in ("SK_Vitec", "SK_Vitec_Mesh")]
    for obj in dst.objects:
        bpy.context.scene.collection.objects.link(obj)
    # Appended data is local; drop the library entries so the file can be saved.
    for lib in list(bpy.data.libraries):
        bpy.data.libraries.remove(lib)
    arm = bpy.data.objects["SK_Vitec"]
    mesh = bpy.data.objects["SK_Vitec_Mesh"]
    bake_actions(arm)
    hg.save_blend(path)
    export_character(arm, mesh)
    return arm, mesh


if __name__ == "__main__" or True:
    if globals().get("VITEC_REBAKE"):
        ARM, MESH = rebake()
    else:
        ARM = build_rig()
