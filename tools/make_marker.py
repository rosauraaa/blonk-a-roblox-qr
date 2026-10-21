"""Genera el marcador QR personalizado de Bonk-a-Blox (cartel imprimible).

El QR apunta a la pagina del juego, asi que al escanearlo con la camara normal del
telefono se abre el juego, y el juego usa el cartel completo como marcador de RA.
El render de Blender, el titulo, las nubes y el confeti dan al rastreador muchos
puntos unicos (un QR solo es demasiado repetitivo).

Uso:
    pip install qrcode pillow
    blender -b -P blender/render_marker_art.py   # solo si cambian los modelos
    python tools/make_marker.py [url]
Despues hay que recompilar assets/marker/marker.mind con tools/compile-marker.html.
"""
import math
import os
import random
import sys

import qrcode
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = sys.argv[1] if len(sys.argv) > 1 else "https://rosauraaa.github.io/blonk-a-roblox-qr/"
OUT = os.path.join(ROOT, "assets", "marker", "marker.png")
ART = os.path.join(ROOT, "assets", "marker", "art-island.png")

W, H = 1200, 1560
INK = (20, 20, 28)
WHITE = (255, 255, 255)
RED, BLUE, YELLOW, GREEN, PINK = (255, 59, 59), (47, 128, 255), (255, 201, 60), (76, 217, 100), (255, 79, 163)
COLORS = [RED, BLUE, YELLOW, GREEN, PINK]


def font(size, names=("impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf")):
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def block(d, box, color, edge=5):
    """Bloque con brillo arriba-izquierda y sombra abajo-derecha (look de juguete)."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=color, outline=INK, width=edge)
    t = max(4, (x1 - x0) // 9)
    d.rectangle([x0 + edge, y0 + edge, x1 - edge, y0 + edge + t], fill=shade(color, 1.25))
    d.rectangle([x0 + edge, y1 - edge - t, x1 - edge, y1 - edge], fill=shade(color, 0.75))


def sky(img):
    top, bottom = (78, 190, 255), (196, 238, 255)
    px = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        px.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bottom)))


def cloud(d, x, y, s):
    for dx, dy, w, h in ((0, 2, 8, 3), (1, 0, 4, 3), (4, 1, 3, 2)):
        d.rectangle([x + dx * s, y + dy * s, x + (dx + w) * s, y + (dy + h) * s], fill=(235, 248, 255))
    d.rectangle([x, y + 4 * s, x + 8 * s, y + 5 * s], fill=(200, 228, 245))


def confetti(img, rng, avoid):
    """Cubitos de colores girados al azar (semilla fija para que el cartel no cambie)."""
    for _ in range(70):
        s = rng.randint(14, 30)
        x, y = rng.randint(60, W - 60), rng.randint(60, H - 60)
        if any(a[0] - 30 < x < a[2] + 30 and a[1] - 30 < y < a[3] + 30 for a in avoid):
            continue
        tile = Image.new("RGBA", (s + 8, s + 8))
        block(ImageDraw.Draw(tile), [4, 4, s + 4, s + 4], rng.choice(COLORS), edge=3)
        tile = tile.rotate(rng.randint(0, 89), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(tile, (x, y))


def title(img, text, cx, cy, size, angle):
    f = font(size)
    widths = [f.getlength(ch) for ch in text]
    tw, th = int(sum(widths)) + 60, size + 60
    layer = Image.new("RGBA", (tw, th))
    d = ImageDraw.Draw(layer)
    x = 30
    for i, (ch, w) in enumerate(zip(text, widths)):
        y = 30 + (8 if i % 2 else 0)  # letras saltarinas
        d.text((x + 9, y + 11), ch, font=f, fill=INK, stroke_width=10, stroke_fill=INK)
        d.text((x, y), ch, font=f, fill=WHITE if ch == "-" else COLORS[i % 5], stroke_width=10, stroke_fill=INK)
        x += w
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))


def sticker(img, text, cx, cy, angle, fill, size=50):
    f = font(size)
    w = int(f.getlength(text)) + 70
    layer = Image.new("RGBA", (w + 20, size + 70))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([10, 14, w + 10, size + 54], 22, fill=INK)
    d.rounded_rectangle([0, 4, w, size + 44], 22, fill=fill, outline=INK, width=6)
    d.text((w // 2, size // 2 + 24), text, font=f, fill=INK, anchor="mm")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))


def burst(img, text, cx, cy, r):
    layer = Image.new("RGBA", (r * 2 + 20, r * 2 + 20))
    d = ImageDraw.Draw(layer)
    pts = [(r + 10 + math.cos(a) * (r if i % 2 else r * 0.62), r + 10 + math.sin(a) * (r if i % 2 else r * 0.62))
           for i, a in enumerate(math.pi * 2 * k / 22 for k in range(22))]
    d.polygon(pts, fill=YELLOW, outline=INK, width=7)
    d.text((r + 10, r + 10), text, font=font(int(r * 0.48)), fill=RED, anchor="mm", stroke_width=5, stroke_fill=INK)
    layer = layer.rotate(-12, resample=Image.BICUBIC)
    img.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))


def frame(d):
    b = 48
    rng = random.Random(7)
    for x0, y0, x1, y1, horizontal in ((0, 0, W, b, True), (0, H - b, W, H, True),
                                       (0, b, b, H - b, False), (W - b, b, W, H - b, False)):
        pos = x0 if horizontal else y0
        end = x1 if horizontal else y1
        while pos < end:
            step = min(rng.choice((b, b, int(b * 1.5), b * 2)), end - pos)
            box = [pos, y0, pos + step, y1] if horizontal else [x0, pos, x1, pos + step]
            block(d, box, rng.choice(COLORS), edge=4)
            pos += step
    return b


def main():
    rng = random.Random(42)
    img = Image.new("RGBA", (W, H))
    sky(img)
    d = ImageDraw.Draw(img)
    for x, y, s in ((90, 300, 16), (760, 110, 12), (930, 1180, 14), (70, 1000, 10), (980, 860, 8)):
        cloud(d, x, y, s)

    # QR en tarjeta blanca con sombra dura
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=11, border=2)
    qr.add_data(URL)
    qr.make(fit=True)
    q = qr.make_image(fill_color=INK, back_color="white").convert("RGBA")
    qx, qy = 90, 290
    card = [qx - 26, qy - 26, qx + q.width + 26, qy + q.height + 26]
    confetti(img, rng, avoid=[card, [60, 60, W - 60, 250], [card[2] + 20, 280, W - 60, 820]])
    d.rounded_rectangle([c + 14 for c in card], 34, fill=INK)
    d.rounded_rectangle(card, 34, fill=WHITE, outline=INK, width=8)
    img.alpha_composite(q, (qx, qy))

    title(img, "BONK-A-BLOX", W // 2, 160, 150, 3)

    # columna derecha: etiqueta e instrucciones
    rx = card[2] + 40
    sticker(img, "¡ESCANÉAME!", rx + 225, 340, 8, YELLOW)
    d.polygon([(card[2] + 10, 415), (rx + 40, 390), (rx + 40, 440)], fill=INK)  # flechita al QR
    steps = (("1", "Escanea", "el QR", RED), ("2", "Apunta", "al cartel", BLUE), ("3", "¡Bonk!", "evita la TNT", GREEN))
    f_big, f_small = font(46), font(30, ("arialbd.ttf", "DejaVuSans-Bold.ttf"))
    for i, (n, a, b, c) in enumerate(steps):
        y = 470 + i * 115
        block(d, [rx + 10, y, rx + 100, y + 90], c, edge=6)
        d.text((rx + 55, y + 45), n, font=font(60), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=INK)
        d.text((rx + 120, y + 4), a, font=f_big, fill=INK)
        d.text((rx + 122, y + 56), b, font=f_small, fill=(40, 50, 70))

    # render de Blender de la isla (abajo, a todo lo ancho)
    art = Image.open(ART).convert("RGBA")
    art = art.crop(art.getbbox())
    rgb = ImageEnhance.Color(ImageEnhance.Brightness(art.convert("RGB")).enhance(1.3)).enhance(1.2)
    art = Image.merge("RGBA", (*rgb.split(), art.split()[3]))
    scale = 590 / art.height  # cabe entre la tarjeta del QR y el pie sin taparlo
    art = art.resize((int(art.width * scale), int(art.height * scale)), Image.LANCZOS)
    ax, ay = (W - art.width) // 2, card[3] + 24
    shadow = Image.new("RGBA", art.size, INK + (0,))
    shadow.putalpha(art.split()[3].point(lambda a: 110 if a > 10 else 0))
    img.alpha_composite(shadow, (ax + 16, ay + 18))
    img.alpha_composite(art, (ax, ay))
    burst(img, "BONK!", W - 190, ay + 110, 95)

    # pie
    fy = H - 48 - 74
    d.rectangle([48, fy, W - 48, H - 48], fill=INK)
    d.text((W // 2, fy + 37), "¡TOCA A LOS BLOXYS ANTES DE QUE SE ESCONDAN!", font=font(42), fill=YELLOW, anchor="mm")

    frame(d)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert("RGB").save(OUT)
    print("OK", OUT, "->", URL)


if __name__ == "__main__":
    main()
