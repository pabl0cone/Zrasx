import bpy
import random
import math
from mathutils import Vector

# ============================================================
#  PROCEDURAL 3D ITEM GENERATOR
#  Python + Blender
# ============================================================

random.seed()

# ------------------------------------------------------------
# LIMPAR CENA
# ------------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes,
    bpy.data.curves,
    bpy.data.materials,
    bpy.data.cameras,
    bpy.data.lights
):
    pass


# ------------------------------------------------------------
# MATERIAIS
# ------------------------------------------------------------

def material(name, color, metallic=0.0, roughness=0.5, emission=None):

    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)

    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 6

    return mat


METALS = [
    material("Titanium", (0.16,0.18,0.20), .9, .22),
    material("Dark Metal", (0.035,0.045,0.055), .95, .18),
    material("Steel", (0.32,0.35,0.38), .85, .28),
    material("Copper", (0.45,0.16,0.07), .9, .25)
]

GLOW = [
    material("Blue Energy", (0.01,0.1,0.2), .2, .2, (0.0,0.4,1.0)),
    material("Cyan Energy", (0.0,0.2,0.2), .2, .18, (0.0,1.0,0.9)),
    material("Purple Energy", (0.15,0.02,0.25), .2, .2, (0.7,0.0,1.0)),
    material("Red Energy", (0.25,0.01,0.01), .2, .2, (1.0,0.02,0.01))
]

GLASS = material(
    "Energy Glass",
    (0.02,0.15,0.2),
    .4,
    .08,
    (0.0,0.4,0.8)
)


# ------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------

def smooth(obj):

    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True


def bevel(obj, amount=0.08, segments=3):

    mod = obj.modifiers.new("Procedural Bevel", 'BEVEL')
    mod.width = amount
    mod.segments = segments


def add_cube(location, scale, mat, bevel_amount=.1):

    bpy.ops.mesh.primitive_cube_add(location=location)

    obj = bpy.context.object
    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    bevel(obj, bevel_amount)
    obj.data.materials.append(mat)

    return obj


def add_cylinder(location, radius, depth, mat, vertices=32):

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location
    )

    obj = bpy.context.object
    obj.data.materials.append(mat)

    bevel(obj, .04)
    smooth(obj)

    return obj


def add_uv_sphere(location, scale, mat):

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        location=location
    )

    obj = bpy.context.object
    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    obj.data.materials.append(mat)
    smooth(obj)

    return obj


# ------------------------------------------------------------
# ANEL
# ------------------------------------------------------------

def ring(z, radius, thickness, mat):

    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        major_segments=48,
        minor_segments=12,
        location=(0,0,z)
    )

    obj = bpy.context.object
    obj.data.materials.append(mat)

    smooth(obj)

    return obj


# ------------------------------------------------------------
# DETALHES
# ------------------------------------------------------------

def random_panel():

    side = random.choice([-1, 1])

    x = side * random.uniform(.75, 1.0)

    panel = add_cube(
        (x, 0, random.uniform(-.1,.3)),
        (.04, random.uniform(.25,.5), random.uniform(.2,.5)),
        random.choice(METALS),
        .03
    )

    panel.rotation_euler[1] = random.uniform(-.25,.25)

    return panel


def energy_core():

    core = add_uv_sphere(
        (0,0,0),
        (.42,.42,.42),
        random.choice(GLOW)
    )

    ring(0,.48,.045,random.choice(GLOW))
    ring(0,.58,.025,random.choice(GLOW))

    return core


def antenna():

    side = random.choice([-1,1])

    base = add_cylinder(
        (side*.65,0,.65),
        .09,
        .25,
        random.choice(METALS)
    )

    base.rotation_euler[1] = random.uniform(-.4,.4)

    tip = add_uv_sphere(
        (side*.72,0,.9),
        (.07,.07,.07),
        random.choice(GLOW)
    )

    return base, tip


# ------------------------------------------------------------
# GERADOR PRINCIPAL
# ------------------------------------------------------------

def generate_item():

    # Corpo principal
    body_type = random.choice([
        "cube",
        "cylinder",
        "sphere"
    ])

    main_mat = random.choice(METALS)

    if body_type == "cube":

        body = add_cube(
            (0,0,0),
            (
                random.uniform(.7,1.0),
                random.uniform(.7,1.0),
                random.uniform(.7,1.1)
            ),
            main_mat,
            .12
        )

    elif body_type == "cylinder":

        body = add_cylinder(
            (0,0,0),
            random.uniform(.7,1.0),
            random.uniform(1.2,2.0),
            main_mat,
            random.choice([8,12,16,32])
        )

    else:

        body = add_uv_sphere(
            (0,0,0),
            (
                random.uniform(.7,1.0),
                random.uniform(.7,1.0),
                random.uniform(.7,1.0)
            ),
            main_mat
        )

    # --------------------------------------------------------
    # NÚCLEO
    # --------------------------------------------------------

    if random.random() < .85:
        energy_core()

    # --------------------------------------------------------
    # ANÉIS
    # --------------------------------------------------------

    for _ in range(random.randint(1,4)):

        z = random.uniform(-.8,.8)
        radius = random.uniform(.65,1.15)

        ring(
            z,
            radius,
            random.uniform(.015,.07),
            random.choice(GLOW + METALS)
        )

    # --------------------------------------------------------
    # PAINÉIS
    # --------------------------------------------------------

    for _ in range(random.randint(2,7)):
        random_panel()

    # --------------------------------------------------------
    # ANTENAS
    # --------------------------------------------------------

    for _ in range(random.randint(0,4)):
        antenna()

    # --------------------------------------------------------
    # PARAFUSOS
    # --------------------------------------------------------

    for _ in range(random.randint(4,16)):

        angle = random.uniform(0, math.tau)

        radius = random.uniform(.65,1.0)

        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        add_cylinder(
            (x,y,random.uniform(-.8,.8)),
            .035,
            .06,
            random.choice(METALS),
            12
        )

    # --------------------------------------------------------
    # PLACAS SUPERIORES
    # --------------------------------------------------------

    for _ in range(random.randint(1,5)):

        x = random.uniform(-.7,.7)
        y = random.uniform(-.7,.7)

        plate = add_cube(
            (x,y,random.uniform(.7,1.0)),
            (
                random.uniform(.08,.25),
                random.uniform(.08,.25),
                .025
            ),
            random.choice(METALS),
            .02
        )

        plate.rotation_euler.z = random.uniform(0,math.tau)

    # --------------------------------------------------------
    # ROTAÇÃO ALEATÓRIA
    # --------------------------------------------------------

    for obj in bpy.context.scene.objects:

        if obj.type == 'MESH':

            obj.rotation_euler.x += random.uniform(-.15,.15)
            obj.rotation_euler.y += random.uniform(-.15,.15)
            obj.rotation_euler.z += random.uniform(-.15,.15)


# ------------------------------------------------------------
# GERAR
# ------------------------------------------------------------

generate_item()


# ============================================================
# CHÃO
# ============================================================

floor_mat = material(
    "Floor",
    (.015,.018,.022),
    .3,
    .35
)

add_cube(
    (0,0,-1.15),
    (4,4,.1),
    floor_mat,
    .03
)


# ============================================================
# ILUMINAÇÃO
# ============================================================

bpy.ops.object.light_add(
    type='AREA',
    location=(4,-4,5)
)

key = bpy.context.object
key.data.energy = 900
key.data.shape = 'DISK'
key.data.size = 4

key.rotation_euler = (
    math.radians(25),
    0,
    math.radians(45)
)


bpy.ops.object.light_add(
    type='AREA',
    location=(-4,2,3)
)

fill = bpy.context.object
fill.data.energy = 600
fill.data.size = 3


# ============================================================
# CÂMERA
# ============================================================

bpy.ops.object.camera_add(
    location=(4,-5,3)
)

camera = bpy.context.object

bpy.context.scene.camera = camera


def point_camera(camera, target):

    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat(
        '-Z',
        'Y'
    ).to_euler()


point_camera(camera,(0,0,0))


# ============================================================
# WORLD
# ============================================================

world = bpy.context.scene.world

world.color = (0.005,0.005,0.008)

world.use_nodes = True

bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (
    .003,.005,.008,1
)

bg.inputs["Strength"].default_value = .15


# ============================================================
# RENDER
# ============================================================

scene = bpy.context.scene

scene.render.engine = 'BLENDER_EEVEE_NEXT'

scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = 'PNG'

scene.render.filepath = "//generated_item.png"

bpy.ops.wm.save_as_mainfile(
    filepath="//procedural_item.blend"
)

bpy.ops.render.render(
    write_still=True
)

print("======================================")
print(" ITEM 3D GERADO COM SUCESSO")
print(" Arquivo: procedural_item.blend")
print(" Render: generated_item.png")
print("======================================")