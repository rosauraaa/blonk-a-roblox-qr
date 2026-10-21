"""Render de la escena del juego para ilustrar el marcador (fondo transparente).

Uso (desde la raiz del repo):
    blender -b -P blender/render_marker_art.py

Salida:
    assets/marker/art-island.png  (lo usa tools/make_marker.py)
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_models import HOLE_X, ROOT, build_hammer, build_island, build_tnt, reset  # noqa: E402

OUT = os.path.join(ROOT, "assets", "marker", "art-island.png")
KENNEY = os.path.join(ROOT, "assets", "models", "kenney")


def character(name, x, z, yaw=0.0, y=0.0):
    bpy.ops.import_scene.gltf(filepath=os.path.join(KENNEY, f"character-{name}.glb"))
    root = bpy.context.selected_objects[0]
    while root.parent:
        root = root.parent
    root.scale = (0.11, 0.11, 0.11)  # los personajes de Kenney miden 2.7 u de alto
    root.location = (x, y, z)
    root.rotation_euler = (0, 0, yaw)


reset()
build_island()
character("a", HOLE_X[0], -0.04, math.radians(-18))   # asomado
character("e", HOLE_X[1], -0.15)                      # recibiendo el bonk
tnt = build_tnt()                                     # la TNT sale del hoyo amarillo
tnt.location = (HOLE_X[2], 0, -0.03)
tnt.rotation_euler = (0, 0, math.radians(20))
character("k", -0.40, 0.0, math.radians(25), y=-0.2)  # uno parado en la orilla
hammer = build_hammer()
hammer.location = (0.24, 0, 0.1)  # la cabeza del martillo queda sobre el bloxy del centro
hammer.rotation_euler = (0, math.radians(-55), 0)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "TEXTURE"
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = "BOTH"
shading.show_object_outline = True
shading.object_outline_color = (0.02, 0.02, 0.03)
scene.render.resolution_x, scene.render.resolution_y = 1600, 1100
scene.render.film_transparent = True

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.32, -1.5, 0.82)
cam.rotation_euler = (math.radians(64), 0, math.radians(11))
cam_data.lens = 42
scene.camera = cam
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("OK", OUT)
