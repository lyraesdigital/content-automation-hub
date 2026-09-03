"""
Genera la imagen final de Facebook combinando UNA de 3 plantillas de fondo
fijas (dibujadas con PIL, sin IA) + el texto motivacional que Gemini ya
genero en conceptos.json.

Ventaja sobre generar la imagen completa con IA: cero limite de cuota,
gratis, instantaneo, 100% confiable. Solo el texto cambia cada vez.

Uso:
    python compose_image.py --conceptos facebook-images/output/motivacion_.../conceptos.json --template 1
"""
import json
import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = (1080, 1080)  # tamaño estandar de post cuadrado Facebook/Instagram

PALETAS = {
    1: {"bg": (26, 11, 46), "bg2": (13, 6, 32), "accent": (255, 45, 149), "text": (240, 230, 255)},
    2: {"bg": (20, 40, 45), "bg2": (10, 20, 25), "accent": (255, 189, 89), "text": (250, 245, 235)},
    3: {"bg": (35, 25, 20), "bg2": (18, 12, 10), "accent": (230, 200, 160), "text": (250, 245, 235)},
}


def dibujar_fondo(paleta):
    img = Image.new("RGB", SIZE, paleta["bg"])
    draw = ImageDraw.Draw(img)
    # gradiente diagonal simple
    for y in range(SIZE[1]):
        t = y / SIZE[1]
        r = int(paleta["bg"][0] * (1 - t) + paleta["bg2"][0] * t)
        g = int(paleta["bg"][1] * (1 - t) + paleta["bg2"][1] * t)
        b = int(paleta["bg"][2] * (1 - t) + paleta["bg2"][2] * t)
        draw.line([(0, y), (SIZE[0], y)], fill=(r, g, b))
    # franja de acento decorativa arriba
    draw.rectangle([0, 0, SIZE[0], 14], fill=paleta["accent"])
    draw.rectangle([0, SIZE[1] - 14, SIZE[0], SIZE[1]], fill=paleta["accent"])
    return img


def cargar_fuente(tamano):
    rutas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for ruta in rutas:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def escribir_texto_centrado(draw, texto, paleta):
    palabras = textwrap.wrap(texto, width=22)
    tamano_fuente = 64 if len(palabras) <= 4 else 52
    fuente = cargar_fuente(tamano_fuente)

    alto_linea = tamano_fuente + 18
    alto_total = alto_linea * len(palabras)
    y = (SIZE[1] - alto_total) // 2

    for linea in palabras:
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        ancho = bbox[2] - bbox[0]
        x = (SIZE[0] - ancho) // 2
        # sombra sutil para legibilidad
        draw.text((x + 3, y + 3), linea, font=fuente, fill=(0, 0, 0))
        draw.text((x, y), linea, font=fuente, fill=paleta["text"])
        y += alto_linea


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conceptos", required=True)
    parser.add_argument("--template", type=int, choices=[1, 2, 3], default=1)
    args = parser.parse_args()

    conceptos_path = Path(args.conceptos)
    data = json.loads(conceptos_path.read_text())
    conceptos = data.get("conceptos", [])

    out_dir = conceptos_path.parent / "imagenes"
    out_dir.mkdir(parents=True, exist_ok=True)

    paleta = PALETAS[args.template]

    for i, concepto in enumerate(conceptos):
        texto = concepto.get("texto_imagen", "")
        img = dibujar_fondo(paleta)
        draw = ImageDraw.Draw(img)
        escribir_texto_centrado(draw, texto, paleta)

        out_path = out_dir / f"post_{i}_template{args.template}.png"
        img.save(out_path)
        print(f"Imagen generada: {out_path}")


if __name__ == "__main__":
    main()
