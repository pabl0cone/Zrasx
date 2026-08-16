# ============================================================
#  ██████╗ ██████╗     ██████╗ ███████╗███╗   ██╗
#  ██╔══██╗╚════██╗    ╚════██╗██╔════╝████╗  ██║
#  ██████╔╝ ███████║     █████╔╝█████╗  ██╔██╗ ██║
#  ██╔═══╝  ██╔══██║    ██╔═══╝ ██╔══╝  ██║╚██╗██║
#  ██║     ██████╔╝    ███████╗███████╗██║ ╚████║
#  ╚═╝     ╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═══╝
#
#              PROCEDURAL FORGE X
#          ADVANCED 3D GENERATION SYSTEM
#
# Python / Blender
# Designed as a foundation for large procedural projects.
#
# ============================================================

import bpy
import math
import random
import os
import json
import hashlib

from mathutils import Vector, Euler


# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "seed": 928371,
    "project_name": "PROCEDURAL_FORGE",
    "object_type": "SCIFI_REACTOR",
    "complexity": 5,
    "detail_density": 0.75,
    "generate_lights": True,
    "generate_camera": True,
    "generate_floor": True,
    "render": True,
    "save_blend": True,
    "save_render": True,
    "resolution": 900,
    "batch_mode": False,
    "batch_count": 1,
    "output_folder": "//procedural_output",
    "enable_lod": True,
    "enable_metadata": True,
}


# ============================================================
# GLOBAL STATE
# ============================================================

RNG = random.Random(CONFIG["seed"])

COLLECTIONS = {}

MATERIALS = {}

GENERATED_OBJECTS = []

METADATA = {
    "generator": "Procedural Forge X",
    "version": "1.0",
    "seed": CONFIG["seed"],
    "objects": [],
}


# ============================================================
# RANDOM HELPERS
# ============================================================

def rand(a, b):
    return RNG.uniform(a, b)


def randi(a, b):
    return RNG.randint(a, b)


def chance(value):
    return RNG.random() < value


def choice(items):
    return RNG.choice(items)


def sign():
    return -1 if chance(0.5) else 1


def random_vector(scale=1.0):
    return Vector((
        rand(-scale, scale),
        rand(-scale, scale),
        rand(-scale, scale)
    ))


def random_color():
    return (
        rand(0.02, 0.8),
        rand(0.02, 0.8),
        rand(0.02, 0.8)
    )


# ============================================================
# HASH / SEED SYSTEM
# ============================================================

def seed_from_string(text):
    value = int(
        hashlib.sha256(
            text.encode()
        ).hexdigest()[:8],
        16
    )
    return value


def set_seed(seed):
    global RNG
    RNG = random.Random(seed)
    CONFIG["seed"] = seed
    METADATA["seed"] = seed


# ============================================================
# SCENE CLEANUP
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


# ============================================================
# COLLECTION SYSTEM
# ============================================================

def create_collection(name):
    if name in COLLECTIONS:
        return COLLECTIONS[name]

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    COLLECTIONS[name] = collection
    return collection


def move_to_collection(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


# ============================================================
# MATERIAL ENGINE
# ============================================================

def set_principled_bsdf_input(bsdf_node, input_name, value):
    """Safely set a Principled BSDF node input across Blender versions (3.x & 4.x+)."""
    socket_mappings = {
        "Base Color": ["Base Color"],
        "Metallic": ["Metallic"],
        "Roughness": ["Roughness"],
        "Emission Color": ["Emission Color", "Emission"],
        "Emission Strength": ["Emission Strength"]
    }
    possible_names = socket_mappings.get(input_name, [input_name])
    for name in possible_names:
        if name in bsdf_node.inputs:
            bsdf_node.inputs[name].default_value = value
            return True
    return False


def create_material(
    name,
    base_color,
    metallic=0.0,
    roughness=0.5,
    emission=None,
    emission_strength=0.0
):
    if name in MATERIALS:
        return MATERIALS[name]

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        set_principled_bsdf_input(bsdf, "Base Color", (*base_color, 1))
        set_principled_bsdf_input(bsdf, "Metallic", metallic)
        set_principled_bsdf_input(bsdf, "Roughness", roughness)

        if emission:
            set_principled_bsdf_input(bsdf, "Emission Color", (*emission, 1))
            set_principled_bsdf_input(bsdf, "Emission Strength", emission_strength)

    MATERIALS[name] = mat
    return mat


def create_material_library():
    MATERIALS.clear()

    create_material(
        "MAT_BLACK_METAL",
        (0.012, 0.015, 0.02),
        0.95,
        0.18
    )

    create_material(
        "MAT_DARK_STEEL",
        (0.06, 0.07, 0.08),
        0.9,
        0.25
    )

    create_material(
        "MAT_STEEL",
        (0.3, 0.32, 0.35),
        0.85,
        0.3
    )

    create_material(
        "MAT_TITANIUM",
        (0.18, 0.2, 0.22),
        0.95,
        0.2
    )

    create_material(
        "MAT_COPPER",
        (0.35, 0.09, 0.035),
        0.9,
        0.24
    )

    create_material(
        "MAT_GOLD",
        (0.55, 0.32, 0.06),
        0.9,
        0.2
    )

    create_material(
        "MAT_WHITE",
        (0.65, 0.67, 0.7),
        0.7,
        0.28
    )

    create_material(
        "MAT_RUBBER",
        (0.008, 0.008, 0.009),
        0.05,
        0.72
    )

    create_material(
        "MAT_GLASS",
        (0.02, 0.12, 0.16),
        0.45,
        0.08,
        (0.0, 0.25, 0.4),
        2
    )

    create_material(
        "MAT_ENERGY_BLUE",
        (0.0, 0.04, 0.08),
        0.25,
        0.12,
        (0.0, 0.35, 1.0),
        8
    )

    create_material(
        "MAT_ENERGY_CYAN",
        (0.0, 0.07, 0.06),
        0.2,
        0.12,
        (0.0, 1.0, 0.75),
        10
    )

    create_material(
        "MAT_ENERGY_PURPLE",
        (0.07, 0.0, 0.12),
        0.2,
        0.12,
        (0.6, 0.0, 1.0),
        10
    )

    create_material(
        "MAT_ENERGY_RED",
        (0.1, 0.0, 0.0),
        0.2,
        0.15,
        (1.0, 0.01, 0.0),
        10
    )


# ============================================================
# MATERIAL ACCESS
# ============================================================

def mat(name):
    return MATERIALS.get(
        name,
        MATERIALS.get("MAT_DARK_STEEL")
    )


def energy_material():
    return choice([
        mat("MAT_ENERGY_BLUE"),
        mat("MAT_ENERGY_CYAN"),
        mat("MAT_ENERGY_PURPLE"),
        mat("MAT_ENERGY_RED")
    ])


def metal_material():
    return choice([
        mat("MAT_BLACK_METAL"),
        mat("MAT_DARK_STEEL"),
        mat("MAT_STEEL"),
        mat("MAT_TITANIUM")
    ])


# ============================================================
# OBJECT REGISTRATION
# ============================================================

def register_object(obj, category="generic"):
    GENERATED_OBJECTS.append(obj)
    obj["PF_CATEGORY"] = category
    obj["PF_SEED"] = CONFIG["seed"]

    obj_name = getattr(obj, "name", str(obj))
    METADATA["objects"].append({
        "name": obj_name,
        "category": category
    })

    return obj


# ============================================================
# MODIFIERS
# ============================================================

def add_bevel(
    obj,
    width=0.05,
    segments=3
):
    modifier = obj.modifiers.new(
        "PF_BEVEL",
        "BEVEL"
    )
    modifier.width = width
    modifier.segments = segments
    return modifier


def add_weighted_normals(obj):
    try:
        modifier = obj.modifiers.new(
            "PF_NORMALS",
            "WEIGHTED_NORMAL"
        )
        return modifier
    except Exception:
        pass


def smooth_mesh(obj):
    if getattr(obj, "type", None) != 'MESH':
        return

    try:
        if hasattr(bpy.ops.object, "shade_smooth"):
            prev_active = bpy.context.view_layer.objects.active
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            if prev_active:
                bpy.context.view_layer.objects.active = prev_active
        else:
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
    except Exception:
        if hasattr(obj, "data") and hasattr(obj.data, "polygons"):
            for polygon in obj.data.polygons:
                polygon.use_smooth = True


# ============================================================
# BASIC PRIMITIVES
# ============================================================

def cube(
    name,
    location,
    scale,
    material,
    bevel=0.05,
    collection="FORGE_GEOMETRY"
):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    if bevel:
        add_bevel(obj, bevel)

    add_weighted_normals(obj)

    if material:
        obj.data.materials.append(material)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(obj, "cube")


def cylinder(
    name,
    location,
    radius,
    depth,
    material,
    vertices=32,
    collection="FORGE_GEOMETRY"
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location
    )

    obj = bpy.context.object
    obj.name = name

    if material:
        obj.data.materials.append(material)

    add_bevel(
        obj,
        min(radius * 0.12, 0.08),
        3
    )

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(obj, "cylinder")


def sphere(
    name,
    location,
    scale,
    material,
    collection="FORGE_GEOMETRY"
):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=20,
        location=location
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    if material:
        obj.data.materials.append(material)

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(obj, "sphere")


def torus(
    name,
    location,
    major,
    minor,
    material,
    rotation=(0, 0, 0)
):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=48,
        minor_segments=12,
        location=location,
        rotation=rotation
    )

    obj = bpy.context.object
    obj.name = name

    if material:
        obj.data.materials.append(material)

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection("FORGE_DETAILS")
    )

    return register_object(obj, "ring")


# ============================================================
# PANEL GENERATOR
# ============================================================

def panel(location, scale, rotation=(0, 0, 0)):
    obj = cube(
        "PF_PANEL",
        location,
        scale,
        metal_material(),
        bevel=min(scale) * 0.2
    )
    obj.rotation_euler = rotation
    return obj


# ============================================================
# BOLT GENERATOR
# ============================================================

def bolt(location, scale=1.0):
    obj = cylinder(
        "PF_BOLT",
        location,
        0.035 * scale,
        0.055 * scale,
        metal_material(),
        8
    )
    return obj


# ============================================================
# BOLT ARRAY
# ============================================================

def bolt_ring(radius, count, z=0):
    for i in range(count):
        angle = math.tau * i / count
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        bolt(
            (x, y, z),
            rand(0.7, 1.4)
        )


# ============================================================
# ENERGY RING SYSTEM
# ============================================================

def energy_ring(z, radius, thickness):
    return torus(
        "PF_ENERGY_RING",
        (0, 0, z),
        radius,
        thickness,
        energy_material()
    )


def energy_core():
    core_material = energy_material()

    core = sphere(
        "PF_CORE",
        (0, 0, 0),
        (
            rand(0.25, 0.42),
            rand(0.25, 0.42),
            rand(0.25, 0.55)
        ),
        core_material
    )

    for _ in range(randi(2, 5)):
        energy_ring(
            rand(-0.5, 0.5),
            rand(0.42, 0.72),
            rand(0.015, 0.045)
        )

    return core


# ============================================================
# CABLE SYSTEM
# ============================================================

def cable(start, end, radius=0.025):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    length = direction.length
    middle = (start + end) / 2

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=radius,
        depth=length,
        location=middle
    )

    obj = bpy.context.object
    obj.name = "PF_CABLE"
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')

    mat_rubber = mat("MAT_RUBBER")
    if mat_rubber:
        obj.data.materials.append(mat_rubber)

    move_to_collection(
        obj,
        create_collection("FORGE_CABLES")
    )

    return register_object(obj, "cable")


# ============================================================
# RANDOM CABLE NETWORK
# ============================================================

def generate_cables():
    amount = int(5 + CONFIG["complexity"] * 3)

    for _ in range(amount):
        angle1 = rand(0, math.tau)
        angle2 = angle1 + rand(-0.8, 0.8)

        radius1 = rand(0.6, 1.3)
        radius2 = rand(0.6, 1.3)

        z1 = rand(-0.9, 0.9)
        z2 = rand(-0.9, 0.9)

        p1 = (
            math.cos(angle1) * radius1,
            math.sin(angle1) * radius1,
            z1
        )

        p2 = (
            math.cos(angle2) * radius2,
            math.sin(angle2) * radius2,
            z2
        )

        cable(
            p1,
            p2,
            rand(0.015, 0.035)
        )


# ============================================================
# ANTENNA SYSTEM
# ============================================================

def antenna(angle, height):
    radius = 1.0
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius

    base = cylinder(
        "PF_ANTENNA_BASE",
        (x, y, 0),
        0.1,
        0.18,
        metal_material()
    )

    pole = cylinder(
        "PF_ANTENNA",
        (x, y, height / 2),
        0.025,
        height,
        metal_material(),
        12
    )

    tip = sphere(
        "PF_ANTENNA_LIGHT",
        (x, y, height),
        (0.07, 0.07, 0.07),
        energy_material()
    )

    return pole


# ============================================================
# EXTERNAL MODULE
# ============================================================

def external_module(angle, distance, z):
    x = math.cos(angle) * distance
    y = math.sin(angle) * distance

    module = cube(
        "PF_MODULE",
        (x, y, z),
        (
            rand(0.15, 0.3),
            rand(0.15, 0.3),
            rand(0.25, 0.5)
        ),
        metal_material(),
        0.05
    )

    module.rotation_euler.z = angle

    for _ in range(randi(2, 5)):
        px = x + rand(-0.15, 0.15)
        py = y + rand(-0.15, 0.15)
        pz = z + rand(-0.2, 0.2)

        sphere(
            "PF_MODULE_LIGHT",
            (px, py, pz),
            (0.025, 0.025, 0.025),
            energy_material()
        )


# ============================================================
# INDUSTRIAL DETAILS
# ============================================================

def generate_industrial_details():
    amount = int(
        10
        * CONFIG["detail_density"]
        * CONFIG["complexity"]
    )

    for _ in range(amount):
        angle = rand(0, math.tau)
        radius = rand(0.7, 1.5)
        z = rand(-0.9, 0.9)

        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        choice_type = choice([
            "panel",
            "bolt",
            "module",
            "light"
        ])

        if choice_type == "panel":
            panel(
                (x, y, z),
                (
                    rand(0.03, 0.12),
                    rand(0.1, 0.25),
                    rand(0.1, 0.35)
                ),
                (
                    rand(-0.2, 0.2),
                    rand(-0.2, 0.2),
                    angle
                )
            )

        elif choice_type == "bolt":
            bolt(
                (x, y, z),
                rand(0.7, 1.5)
            )

        elif choice_type == "module":
            external_module(
                angle,
                radius,
                z
            )

        else:
            sphere(
                "PF_STATUS_LIGHT",
                (x, y, z),
                (0.025, 0.025, 0.025),
                energy_material()
            )


# ============================================================
# REACTOR BODY
# ============================================================

def generate_reactor():
    body_radius = rand(0.8, 1.25)
    body_height = rand(1.4, 2.4)

    body = cylinder(
        "PF_REACTOR_BODY",
        (0, 0, 0),
        body_radius,
        body_height,
        metal_material(),
        choice([12, 16, 24, 32])
    )

    # Base
    cylinder(
        "PF_REACTOR_BASE",
        (0, 0, -body_height / 2 - 0.12),
        body_radius * 1.12,
        0.22,
        mat("MAT_BLACK_METAL"),
        32
    )

    # Top
    cylinder(
        "PF_REACTOR_TOP",
        (0, 0, body_height / 2 + 0.12),
        body_radius * 1.08,
        0.18,
        mat("MAT_DARK_STEEL"),
        32
    )

    # Central core
    energy_core()

    # Main rings
    ring_count = randi(3, 7)
    for i in range(ring_count):
        z = (
            -body_height / 2
            + body_height
            * i
            / max(ring_count - 1, 1)
        )

        torus(
            "PF_BODY_RING",
            (0, 0, z),
            body_radius * rand(0.98, 1.08),
            rand(0.025, 0.065),
            choice([
                metal_material(),
                energy_material()
            ])
        )

    # Bolts
    bolt_ring(
        body_radius * 1.02,
        randi(8, 16),
        body_height / 2 + 0.22
    )

    bolt_ring(
        body_radius * 1.02,
        randi(8, 16),
        -body_height / 2 - 0.22
    )

    # External modules
    for _ in range(randi(4, 10)):
        external_module(
            rand(0, math.tau),
            body_radius * rand(1.05, 1.45),
            rand(-body_height * 0.4, body_height * 0.4)
        )

    # Antennas
    for _ in range(randi(1, 5)):
        antenna(
            rand(0, math.tau),
            rand(1.0, 2.2)
        )

    # Cables
    generate_cables()

    # Details
    generate_industrial_details()

    return body


# ============================================================
# LOD SYSTEM
# ============================================================

def create_lod(obj, levels=3):
    """
    Creates Level of Detail (LOD) versions of a mesh object using Decimate modifier.
    Returns a list of created LOD objects.
    """
    if not CONFIG.get("enable_lod", True) or getattr(obj, "type", None) != 'MESH':
        return []

    lod_objects = []
    ratios = [0.5, 0.25, 0.1]
    lod_collection = create_collection("FORGE_LODS")

    for idx, ratio in enumerate(ratios[:levels]):
        lod_name = f"{obj.name}_LOD{idx+1}"
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = lod_name

        mod = lod_obj.modifiers.new(name=f"PF_DECIMATE_LOD{idx+1}", type='DECIMATE')
        mod.ratio = ratio
        lod_obj.hide_viewport = True

        move_to_collection(lod_obj, lod_collection)
        register_object(lod_obj, f"{obj.get('PF_CATEGORY', 'generic')}_LOD{idx+1}")
        lod_objects.append(lod_obj)

    return lod_objects


# ============================================================
# FLOOR / STUDIO BACKDROP
# ============================================================

def generate_floor():
    """Generates a ground plane / studio backdrop with metallic panel material."""
    if not CONFIG.get("generate_floor", True):
        return None

    floor_mat = create_material("MAT_FLOOR", (0.02, 0.02, 0.025), metallic=0.8, roughness=0.4)

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -2.0))
    floor = bpy.context.object
    floor.name = "PF_FLOOR"
    if floor_mat:
        floor.data.materials.append(floor_mat)

    move_to_collection(floor, create_collection("FORGE_ENVIRONMENT"))
    register_object(floor, "environment_floor")
    return floor


# ============================================================
# LIGHTING SYSTEM
# ============================================================

def generate_lighting():
    """Generates a 3-point lighting setup (Key, Fill, Rim) with color temperature accent lights."""
    if not CONFIG.get("generate_lights", True):
        return []

    light_collection = create_collection("FORGE_LIGHTS")
    lights = []

    # Key Light
    key_data = bpy.data.lights.new(name="PF_KeyLight_Data", type='AREA')
    key_data.energy = 800.0
    key_data.size = 5.0
    key_data.color = (1.0, 0.95, 0.85)
    key_obj = bpy.data.objects.new("PF_KeyLight", key_data)
    key_obj.location = (4.0, -4.0, 5.0)
    key_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
    light_collection.objects.link(key_obj)
    register_object(key_obj, "light_key")
    lights.append(key_obj)

    # Fill Light
    fill_data = bpy.data.lights.new(name="PF_FillLight_Data", type='AREA')
    fill_data.energy = 400.0
    fill_data.size = 8.0
    fill_data.color = (0.4, 0.7, 1.0)
    fill_obj = bpy.data.objects.new("PF_FillLight", fill_data)
    fill_obj.location = (-5.0, -3.0, 3.0)
    fill_obj.rotation_euler = (math.radians(30), 0, math.radians(-60))
    light_collection.objects.link(fill_obj)
    register_object(fill_obj, "light_fill")
    lights.append(fill_obj)

    # Rim Light
    rim_data = bpy.data.lights.new(name="PF_RimLight_Data", type='POINT')
    rim_data.energy = 1200.0
    rim_data.color = (0.0, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("PF_RimLight", rim_data)
    rim_obj.location = (0.0, 5.0, 4.0)
    light_collection.objects.link(rim_obj)
    register_object(rim_obj, "light_rim")
    lights.append(rim_obj)

    return lights


# ============================================================
# CAMERA SYSTEM
# ============================================================

def generate_camera():
    """Generates and sets up the primary camera targeting the generated object."""
    if not CONFIG.get("generate_camera", True):
        return None

    cam_collection = create_collection("FORGE_CAMERA")
    cam_data = bpy.data.cameras.new(name="PF_Camera_Data")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("PF_Camera", cam_data)

    cam_obj.location = (6.0, -6.0, 4.0)
    cam_obj.rotation_euler = (math.radians(60), 0, math.radians(45))

    cam_collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    register_object(cam_obj, "camera")
    return cam_obj


# ============================================================
# METADATA EXPORT
# ============================================================

def export_metadata(output_dir):
    """Exports generation metadata (seed, config, object count, timestamp) to JSON."""
    if not CONFIG.get("enable_metadata", True):
        return

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"metadata_seed_{CONFIG['seed']}.json")

    meta = dict(METADATA)
    meta["config"] = CONFIG
    meta["generated_object_count"] = len(GENERATED_OBJECTS)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)

    print(f"[Procedural Forge] Metadata saved to: {filepath}")


# ============================================================
# RENDER & SAVE SYSTEM
# ============================================================

def render_and_save(output_dir):
    """Configures scene render settings and saves render / .blend file."""
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene

    scene.render.resolution_x = CONFIG.get("resolution", 900)
    scene.render.resolution_y = CONFIG.get("resolution", 900)

    seed = CONFIG["seed"]

    if CONFIG.get("save_blend", True):
        blend_path = os.path.join(output_dir, f"Procedural_Forge_{seed}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend_path))
        print(f"[Procedural Forge] Saved Blend file: {blend_path}")

    if CONFIG.get("render", True) and CONFIG.get("save_render", True):
        render_path = os.path.join(output_dir, f"Procedural_Forge_{seed}.png")
        scene.render.filepath = os.path.abspath(render_path)
        bpy.ops.render.render(write_still=True)
        print(f"[Procedural Forge] Saved Render image: {render_path}")


# ============================================================
# PIPELINE EXECUTION
# ============================================================

def generate_scene(seed=None):
    """Executes the full procedural generation pipeline for a given seed."""
    if seed is not None:
        set_seed(seed)
    else:
        set_seed(CONFIG["seed"])

    print(f"[Procedural Forge] Starting generation with Seed: {CONFIG['seed']}...")

    clear_scene()
    COLLECTIONS.clear()
    MATERIALS.clear()
    GENERATED_OBJECTS.clear()
    METADATA["objects"].clear()
    METADATA["seed"] = CONFIG["seed"]

    create_material_library()

    # Core generation
    main_body = generate_reactor()

    # LOD Generation
    if CONFIG.get("enable_lod", True) and main_body:
        create_lod(main_body)

    # Environment & Lighting & Camera
    generate_floor()
    generate_lighting()
    generate_camera()

    output_dir = bpy.path.abspath(CONFIG.get("output_folder", "//procedural_output"))

    export_metadata(output_dir)

    if CONFIG.get("render", True) or CONFIG.get("save_blend", True):
        render_and_save(output_dir)

    print(f"[Procedural Forge] Generation complete for seed {CONFIG['seed']}!")


def main():
    if CONFIG.get("batch_mode", False):
        batch_count = CONFIG.get("batch_count", 1)
        base_seed = CONFIG["seed"]
        for i in range(batch_count):
            current_seed = base_seed + i * 10007
            generate_scene(current_seed)
    else:
        generate_scene()


if __name__ == "__main__":
    main()
