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


# ============================================================
# SCENE CLEANUP
# ============================================================

def clear_scene():

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in list(
        bpy.data.collections
    ):

        if collection.name != "Collection":

            bpy.data.collections.remove(
                collection
            )


# ============================================================
# COLLECTION SYSTEM
# ============================================================

def create_collection(name):

    if name in COLLECTIONS:
        return COLLECTIONS[name]

    collection = bpy.data.collections.new(name)

    bpy.context.scene.collection.children.link(
        collection
    )

    COLLECTIONS[name] = collection

    return collection


def move_to_collection(obj, collection):

    for c in list(obj.users_collection):
        c.objects.unlink(obj)

    collection.objects.link(obj)


# ============================================================
# MATERIAL ENGINE
# ============================================================

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

    bsdf.inputs[
        "Base Color"
    ].default_value = (
        *base_color,
        1
    )

    bsdf.inputs[
        "Metallic"
    ].default_value = metallic

    bsdf.inputs[
        "Roughness"
    ].default_value = roughness

    if emission:

        bsdf.inputs[
            "Emission Color"
        ].default_value = (
            *emission,
            1
        )

        bsdf.inputs[
            "Emission Strength"
        ].default_value = emission_strength

    MATERIALS[name] = mat

    return mat


def create_material_library():

    MATERIALS.clear()

    create_material(
        "MAT_BLACK_METAL",
        (0.012,0.015,0.02),
        0.95,
        0.18
    )

    create_material(
        "MAT_DARK_STEEL",
        (0.06,0.07,0.08),
        0.9,
        0.25
    )

    create_material(
        "MAT_STEEL",
        (0.3,0.32,0.35),
        0.85,
        0.3
    )

    create_material(
        "MAT_TITANIUM",
        (0.18,0.2,0.22),
        0.95,
        0.2
    )

    create_material(
        "MAT_COPPER",
        (0.35,0.09,0.035),
        0.9,
        0.24
    )

    create_material(
        "MAT_GOLD",
        (0.55,0.32,0.06),
        0.9,
        0.2
    )

    create_material(
        "MAT_WHITE",
        (0.65,0.67,0.7),
        0.7,
        0.28
    )

    create_material(
        "MAT_RUBBER",
        (0.008,0.008,0.009),
        0.05,
        0.72
    )

    create_material(
        "MAT_GLASS",
        (0.02,0.12,0.16),
        0.45,
        0.08,
        (0.0,0.25,0.4),
        2
    )

    create_material(
        "MAT_ENERGY_BLUE",
        (0.0,0.04,0.08),
        0.25,
        0.12,
        (0.0,0.35,1.0),
        8
    )

    create_material(
        "MAT_ENERGY_CYAN",
        (0.0,0.07,0.06),
        0.2,
        0.12,
        (0.0,1.0,0.75),
        10
    )

    create_material(
        "MAT_ENERGY_PURPLE",
        (0.07,0.0,0.12),
        0.2,
        0.12,
        (0.6,0.0,1.0),
        10
    )

    create_material(
        "MAT_ENERGY_RED",
        (0.1,0.0,0.0),
        0.2,
        0.15,
        (1.0,0.01,0.0),
        10
    )


# ============================================================
# MATERIAL ACCESS
# ============================================================

def mat(name):

    return MATERIALS.get(
        name,
        MATERIALS["MAT_DARK_STEEL"]
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

    METADATA["objects"].append({
        "name": obj.name,
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

    except:

        pass


def smooth_mesh(obj):

    if obj.type != 'MESH':
        return

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

    bpy.ops.mesh.primitive_cube_add(
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

    if bevel:
        add_bevel(obj, bevel)

    add_weighted_normals(obj)

    obj.data.materials.append(material)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(
        obj,
        "cube"
    )


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

    obj.data.materials.append(material)

    add_bevel(
        obj,
        min(radius * .12, .08),
        3
    )

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(
        obj,
        "cylinder"
    )


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

    obj.data.materials.append(material)

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection(collection)
    )

    return register_object(
        obj,
        "sphere"
    )


def torus(
    name,
    location,
    major,
    minor,
    material,
    rotation=(0,0,0)
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

    obj.data.materials.append(material)

    smooth_mesh(obj)

    move_to_collection(
        obj,
        create_collection("FORGE_DETAILS")
    )

    return register_object(
        obj,
        "ring"
    )


# ============================================================
# PANEL GENERATOR
# ============================================================

def panel(
    location,
    scale,
    rotation=(0,0,0)
):

    obj = cube(
        "PF_PANEL",
        location,
        scale,
        metal_material(),
        bevel=min(scale) * .2
    )

    obj.rotation_euler = rotation

    return obj


# ============================================================
# BOLT GENERATOR
# ============================================================

def bolt(
    location,
    scale=1.0
):

    obj = cylinder(
        "PF_BOLT",
        location,
        .035 * scale,
        .055 * scale,
        metal_material(),
        8
    )

    return obj


# ============================================================
# BOLT ARRAY
# ============================================================

def bolt_ring(
    radius,
    count,
    z=0
):

    for i in range(count):

        angle = (
            math.tau
            * i
            / count
        )

        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        bolt(
            (x,y,z),
            rand(.7,1.4)
        )


# ============================================================
# ENERGY RING SYSTEM
# ============================================================

def energy_ring(
    z,
    radius,
    thickness
):

    return torus(
        "PF_ENERGY_RING",
        (0,0,z),
        radius,
        thickness,
        energy_material()
    )


def energy_core():

    core_material = energy_material()

    core = sphere(
        "PF_CORE",
        (0,0,0),
        (
            rand(.25,.42),
            rand(.25,.42),
            rand(.25,.55)
        ),
        core_material
    )

    for i in range(
        randi(2,5)
    ):

        energy_ring(
            rand(-.5,.5),
            rand(.42,.72),
            rand(.015,.045)
        )

    return core


# ============================================================
# CABLE SYSTEM
# ============================================================

def cable(
    start,
    end,
    radius=.025
):

    start = Vector(start)
    end = Vector(end)

    direction = end - start

    length = direction.length

    middle = (
        start + end
    ) / 2

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=radius,
        depth=length,
        location=middle
    )

    obj = bpy.context.object

    obj.name = "PF_CABLE"

    obj.rotation_mode = 'QUATERNION'

    obj.rotation_quaternion = (
        direction.to_track_quat(
            'Z',
            'Y'
        )
    )

    obj.data.materials.append(
        mat("MAT_RUBBER")
    )

    move_to_collection(
        obj,
        create_collection("FORGE_CABLES")
    )

    return register_object(
        obj,
        "cable"
    )


# ============================================================
# RANDOM CABLE NETWORK
# ============================================================

def generate_cables():

    amount = int(
        5
        + CONFIG["complexity"] * 3
    )

    for i in range(amount):

        angle1 = rand(
            0,
            math.tau
        )

        angle2 = angle1 + rand(
            -.8,
            .8
        )

        radius1 = rand(
            .6,
            1.3
        )

        radius2 = rand(
            .6,
            1.3
        )

        z1 = rand(
            -.9,
            .9
        )

        z2 = rand(
            -.9,
            .9
        )

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
            rand(.015,.035)
        )


# ============================================================
# ANTENNA SYSTEM
# ============================================================

def antenna(
    angle,
    height
):

    radius = 1.0

    x = math.cos(angle) * radius
    y = math.sin(angle) * radius

    base = cylinder(
        "PF_ANTENNA_BASE",
        (x,y,0),
        .1,
        .18,
        metal_material()
    )

    pole = cylinder(
        "PF_ANTENNA",
        (
            x,
            y,
            height / 2
        ),
        .025,
        height,
        metal_material(),
        12
    )

    tip = sphere(
        "PF_ANTENNA_LIGHT",
        (
            x,
            y,
            height
        ),
        (.07,.07,.07),
        energy_material()
    )

    return pole


# ============================================================
# EXTERNAL MODULE
# ============================================================

def external_module(
    angle,
    distance,
    z
):

    x = math.cos(angle) * distance
    y = math.sin(angle) * distance

    module = cube(
        "PF_MODULE",
        (x,y,z),
        (
            rand(.15,.3),
            rand(.15,.3),
            rand(.25,.5)
        ),
        metal_material(),
        .05
    )

    module.rotation_euler.z = angle

    for i in range(
        randi(2,5)
    ):

        px = x + rand(-.15,.15)
        py = y + rand(-.15,.15)
        pz = z + rand(-.2,.2)

        sphere(
            "PF_MODULE_LIGHT",
            (px,py,pz),
            (.025,.025,.025),
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

    for i in range(amount):

        angle = rand(
            0,
            math.tau
        )

        radius = rand(
            .7,
            1.5
        )

        z = rand(
            -.9,
            .9
        )

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
                (x,y,z),
                (
                    rand(.03,.12),
                    rand(.1,.25),
                    rand(.1,.35)
                ),
                (
                    rand(-.2,.2),
                    rand(-.2,.2),
                    angle
                )
            )

        elif choice_type == "bolt":

            bolt(
                (x,y,z),
                rand(.7,1.5)
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
                (x,y,z),
                (.025,.025,.025),
                energy_material()
            )


# ============================================================
# REACTOR BODY
# ============================================================

def generate_reactor():

    body_radius = rand(
        .8,
        1.25
    )

    body_height = rand(
        1.4,
        2.4
    )

    body = cylinder(
        "PF_REACTOR_BODY",
        (0,0,0),
        body_radius,
        body_height,
        metal_material(),
        choice([
            12,
            16,
            24,
            32
        ])
    )

    # Base

    cylinder(
        "PF_REACTOR_BASE",
        (0,0,-body_height/2-.12),
        body_radius * 1.12,
        .22,
        mat("MAT_BLACK_METAL"),
        32
    )

    # Top

    cylinder(
        "PF_REACTOR_TOP",
        (0,0,body_height/2+.12),
        body_radius * 1.08,
        .18,
        mat("MAT_DARK_STEEL"),
        32
    )

    # Central core

    energy_core()

    # Main rings

    ring_count = randi(
        3,
        7
    )

    for i in range(
        ring_count
    ):

        z = (
            -body_height/2
            + body_height
            * i
            / max(
                ring_count-1,
                1
            )
        )

        torus(
            "PF_BODY_RING",
            (0,0,z),
            body_radius * rand(
                .98,
                1.08
            ),
            rand(.025,.065),
            choice([
                metal_material(),
                energy_material()
            ])
        )

    # Bolts

    bolt_ring(
        body_radius * 1.02,
        randi(8,16),
        body_height/2+.22
    )

    bolt_ring(
        body_radius * 1.02,
        randi(8,16),
        -body_height/2-.22
    )

    # External modules

    for i in range(
        randi(4,10)
    ):

        external_module(
            rand(0,math.tau),
            body_radius * rand(
                1.05,
                1.45
            ),
            rand(
                -body_height*.4,
                body_height*.4
            )
        )

    # Antennas

    for i in range(
        randi(1,5)
    ):

        antenna(
            rand(0,math.tau),
            rand(1.0,2.2)
        )

    # Cables

    generate_cables()

    # Details

    generate_industrial_details()

    return body


# ============================================================
# LOD SYSTEM
# ============================================================

def create_lod