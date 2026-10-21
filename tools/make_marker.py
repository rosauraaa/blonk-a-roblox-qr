"""Genera el marcador QR personalizado de Bonk-a-Blox.

El QR apunta a la pagina del juego, asi que al escanearlo con la camara normal del
telefono se abre el juego, y el juego usa la misma imagen como marcador de RA.
Alrededor del QR van un marco asimetrico y una ilustracion para que el rastreador
tenga puntos unicos (un QR solo es demasiado repetitivo).

Uso:
    pip install qrcode pillow
    python tools/make_marker.py [url]
"""
import os
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = sys.argv[1] if len(sys.argv) > 1 else "https://rosauraaa.github.io/bonk-a-blox-qr/"
OUT = os.path.join(ROOT, "assets", "marker", "marker.png")

W, H = 1000, 1300
INK = (20, 20, 28)
COLORS = [(255, 59, 59), (47, 128, 255), (255, 201, 60), (76, 217, 100), (255, 79, 163)]


def font(size):
    for name in ("impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def blocky_face(d, x, y, s):
    """Carita de bloque estilo pixel-art (no simetrica a proposito)."""
    d.rectangle([x, y, x + 12 * s, y + 12 * s], fill=(255, 205, 148), outline=INK, width=6)
    d.rectangle([x, y, x + 12 * s, y + 3 * s], fill=(110, 60, 30))          # pelo
    d.rectangle([x + 9 * s, y + 3 * s, x + 12 * s, y + 5 * s], fill=(110, 60, 30))
    d.rectangle([x + 3 * s, y + 5 * s, x + 4 * s, y + 7 * s], fill=INK)      # ojos
    d.rectangle([x + 8 * s, y + 5 * s, x + 9 * s, y + 7 * s], fill=INK)
    d.rectangle([x + 3 * s, y + 9 * s, x + 9 * s, y + 10 * s], fill=INK)     # sonrisa
    d.rectangle([x + 2 * s, y + 8 * s, x + 3 * s, y + 9 * s], fill=INK)
    d.rectangle([x + 9 * s, y + 8 * s, x + 10 * s, y + 9 * s], fill=INK)


def hammer(d, x, y, s):
    d.rectangle([x + 4 * s, y + 4 * s, x + 6 * s, y + 16 * s], fill=(198, 134, 66), outline=INK, width=5)
    d.rectangle([x, y, x + 10 * s, y + 5 * s], fill=(255, 79, 163), outline=INK, width=6)
    d.rectangle([x + 2 * s, y, x + 3 * s, y + 5 * s], fill=(255, 255, 255))
    d.rectangle([x + 7 * s, y, x + 8 * s, y + 5 * s], fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # marco grueso de bloques de colores (cada lado con distinto patron)
    b = 60
    for i, x in enumerate(range(0, W, b)):
        d.rectangle([x, 0, x + b, b], fill=COLORS[i % 5], outline=INK, width=4)
    for i, x in enumerate(range(0, W, b * 2)):
        d.rectangle([x, H - b, x + b * 2, H], fill=COLORS[(i * 2 + 1) % 5], outline=INK, width=4)
    for i, y in enumerate(range(b, H - b, b)):
        if i % 3 != 2:
            d.rectangle([0, y, b, y + b], fill=COLORS[(i + 2) % 5], outline=INK, width=4)
    for i, y in enumerate(range(b, H - b, int(b * 1.5))):
        d.rectangle([W - b, y, W, y + int(b * 1.5)], fill=COLORS[(i + 3) % 5], outline=INK, width=4)

    # titulo
    d.rectangle([b + 20, b + 25, W - b - 20, b + 175], fill=INK)
    d.text((W // 2, b + 100), "BONK-A-BLOX", font=font(118), fill=(255, 201, 60), anchor="mm")

    # QR (alto contraste) con marco negro
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=13, border=2)
    qr.add_data(URL)
    qr.make(fit=True)
    q = qr.make_image(fill_color=INK, back_color="white").convert("RGB")
    qx, qy = b + 60, 290
    d.rectangle([qx - 22, qy - 22, qx + q.width + 22, qy + q.height + 22], fill=INK)
    img.paste(q, (qx, qy))

    # ilustraciones asimetricas: carita a la derecha arriba, martillo abajo a la izquierda
    blocky_face(d, qx + q.width + 45, qy + 10, 11)
    hammer(d, b + 50, H - b - 290, 15)
    d.text((W - b - 40, H - b - 70), "¡TOCA Y BONK!", font=font(64), fill=INK, anchor="rs")
    for i, (sx, sy) in enumerate(((qx + q.width + 50, qy + 200), (qx + q.width + 120, qy + 270),
                                   (qx + q.width + 60, qy + 350), (qx + q.width + 130, qy + 440))):
        d.ellipse([sx, sy, sx + 50, sy + 50], fill=COLORS[i], outline=INK, width=5)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("OK", OUT, "->", URL)


if __name__ == "__main__":
    main()
