"""Genera los modelos propios de Bonk-a-Blox (isla, TNT, martillo) y un render de vista previa.

Uso (desde la raiz del repo):
    blender -b -P blender/build_models.py

Salida:
    assets/models/island.glb
    assets/models/tnt.glb
    assets/models/hammer.glb
    docs/preview-modelos.png
"""
import math
import os

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models")
DOCS = os.path.join(ROOT, "docs")

_mats = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()


def mat(name, rgb, rough=0.6):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*rgb, 1)
    _mats[name] = m
    return m


def hexc(h):
    """'#RRGGBB' -> color lineal para Blender."""
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def box(size, loc, material, bevel=0.006, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 2
    return o


def cyl(r, h, loc, material, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.object
    o.data.materials.append(material)
    return o


def text(body, size, loc, material, rot=(math.pi / 2, 0, 0), depth=0.004):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.data.body = body
    o.data.size = size
    o.data.extrude = depth
    o.data.align_x = "CENTER"
    o.data.align_y = "CENTER"
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.data.materials.clear()
    o.data.materials.append(material)
    return o


def join(objs, name):
    for o in objs:
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    bpy.ops.object.shade_flat()
    return o


def export(obj, filename):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(OUT, filename)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True)
    print("OK", path, os.path.getsize(path), "bytes")


# --------------------------------------------------------------------------- isla
HOLE_X = (-0.3, 0.0, 0.3)
HOLE_COLORS = ("#ff3b3b", "#2f80ff", "#ffc93c")  # deben coincidir con los botones 1-2-3 del juego
TOP = 0.0  # la superficie de pasto queda en z=0 (y=0 en three.js)


def build_island():
    grass = mat("grass", hexc("#4cd964"))
    grass_dark = mat("grass_dark", hexc("#2fb34a"))
    dirt = mat("dirt", hexc("#9b6a3c"))
    dirt_dark = mat("dirt_dark", hexc("#6e4523"))
    hole = mat("hole", hexc("#111111"), rough=1)
    trunk = mat("trunk", hexc("#7a4a24"))
    leaf = mat("leaf", hexc("#27ae60"))
    petal = mat("petal", hexc("#ff7eb6"))
    parts = []

    # cuerpo escalonado de la isla flotante
    parts.append(box((1.0, 0.7, 0.06), (0, 0, TOP - 0.03), grass, bevel=0.012))
    parts.append(box((0.98, 0.68, 0.12), (0, 0, TOP - 0.12), dirt))
    parts.append(box((0.76, 0.5, 0.1), (0.02, -0.02, TOP - 0.23), dirt_dark))
    parts.append(box((0.46, 0.3, 0.1), (-0.04, 0.03, TOP - 0.32), dirt))
    parts.append(box((0.18, 0.14, 0.08), (0.05, 0, TOP - 0.40), dirt_dark))

    # hoyos con borde de color
    for x, c in zip(HOLE_X, HOLE_COLORS):
        rim = mat("rim" + c, hexc(c), rough=0.35)
        parts.append(box((0.16, 0.16, 0.004), (x, 0, TOP + 0.001), hole, bevel=0))
        for dx, dy, sx, sy in ((0, 0.09, 0.2, 0.025), (0, -0.09, 0.2, 0.025), (0.09, 0, 0.025, 0.16), (-0.09, 0, 0.025, 0.16)):
            parts.append(box((sx, sy, 0.03), (x + dx, dy, TOP + 0.015), rim, bevel=0.004))

    # studs estilo bloques de juguete
    for ix in range(-4, 5):
        for iy in range(-2, 3):
            x, y = ix * 0.11, iy * 0.12
            if any(abs(x - hx) < 0.15 for hx in HOLE_X) and abs(y) < 0.15:
                continue
            parts.append(cyl(0.022, 0.014, (x, y, TOP + 0.007), grass_dark, verts=12))

    # arbolitos de bloques
    for tx, ty, s in ((-0.42, 0.27, 1.0), (0.43, -0.26, 0.8), (0.44, 0.27, 0.6)):
        parts.append(box((0.04 * s, 0.04 * s, 0.14 * s), (tx, ty, TOP + 0.07 * s), trunk))
        parts.append(box((0.14 * s, 0.14 * s, 0.1 * s), (tx, ty, TOP + 0.17 * s), leaf))
        parts.append(box((0.09 * s, 0.09 * s, 0.07 * s), (tx, ty, TOP + 0.25 * s), leaf))

    # florecitas
    for fx, fy in ((-0.15, -0.27), (0.15, 0.28), (-0.44, -0.25), (0.22, -0.28)):
        parts.append(box((0.012, 0.012, 0.04), (fx, fy, TOP + 0.02), grass_dark, bevel=0))
        parts.append(box((0.035, 0.035, 0.02), (fx, fy, TOP + 0.045), petal, bevel=0.003))

    return join(parts, "Island")


def build_tnt():
    red = mat("tnt_red", hexc("#e53935"))
    band = mat("tnt_band", hexc("#f5f0e1"))
    ink = mat("tnt_ink", hexc("#1b1b1b"))
    parts = [box((0.16, 0.16, 0.16), (0, 0, 0.08), red, bevel=0.01),
             box((0.165, 0.165, 0.05), (0, 0, 0.08), band, bevel=0.004)]
    for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        d = 0.0835
        loc = (math.sin(ang) * d, -math.cos(ang) * d, 0.08)
        parts.append(text("TNT", 0.045, loc, ink, rot=(math.pi / 2, 0, ang)))
    # mecha
    parts.append(cyl(0.008, 0.05, (0, 0, 0.185), ink, verts=8))
    return join(parts, "TNT")


def build_hammer():
    wood = mat("hammer_wood", hexc("#c68642"))
    head = mat("hammer_head", hexc("#ff4fa3"), rough=0.3)
    stripe = mat("hammer_stripe", hexc("#ffffff"))
    # el origen queda en la base del mango para que el swing gire desde la mano
    parts = [box((0.03, 0.03, 0.26), (0, 0, 0.13), wood),
             box((0.17, 0.09, 0.09), (0, 0, 0.29), head, bevel=0.012),
             box((0.03, 0.095, 0.095), (0.05, 0, 0.29), stripe, bevel=0.004),
             box((0.03, 0.095, 0.095), (-0.05, 0, 0.29), stripe, bevel=0.004)]
    return join(parts, "Hammer")


def render_preview(path):
    """Render rapido (Workbench) de los tres modelos propios junto a los personajes de Kenney."""
    kenney = os.path.join(ROOT, "assets", "models", "kenney")
    for i, c in enumerate(("a", "e", "k")):
        bpy.ops.import_scene.gltf(filepath=os.path.join(kenney, f"character-{c}.glb"))
        root = bpy.context.selected_objects[0]
        while root.parent:
            root = root.parent
        root.scale = (0.11, 0.11, 0.11)  # los personajes de Kenney miden 2.7 u de alto
        root.location = (HOLE_X[i], 0, -0.06 if i != 1 else -0.12)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.display.shading.show_shadows = True
    scene.render.resolution_x, scene.render.resolution_y = 1200, 800
    scene.render.film_transparent = True
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.0, -1.55, 0.95)
    cam.rotation_euler = (math.radians(62), 0, 0)
    cam_data.lens = 40
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("OK", path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)

    reset()
    export(build_island(), "island.glb")
    reset()
    export(build_tnt(), "tnt.glb")
    reset()
    export(build_hammer(), "hammer.glb")

    # escena de vista previa para el README
    reset()
    build_island()
    t = build_tnt()
    t.location = (-0.3, 0.2, 0.0)
    h = build_hammer()
    h.location = (0.42, 0.0, 0.12)
    h.rotation_euler = (0, math.radians(-50), 0)
    render_preview(os.path.join(DOCS, "preview-modelos.png"))
