"""
Genera imagenes del personaje virtual (Lyra) usando Gemini 2.5 Flash Image
("Nano Banana" base, gratis) via la misma GEMINI_API_KEY que ya usas para
texto. NO usa la version "Pro" para evitar requerir facturacion.

NOTA: calidad/consistencia algo menor que Nano Banana Pro, pero gratis y
suficiente para validar contenido antes de invertir en algo pago.

Uso:
    python generate_images.py --escena "cafe_manana"
    python generate_images.py --escena "viaje_paisaje" --n 3
"""
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.gemini_retry import generate_with_retry

MODELO_GRATIS = "gemini-2.5-flash-image"

# Descripcion base del personaje - NO cambiar entre corridas, es lo que
# mantiene su identidad visual reconocible en todo el contenido.
LYRA_DESCRIPCION_BASE = """
Personaje ficticio generado por IA, mujer de apariencia ~25 años,
tono de piel calido mediterraneo-latino, ojos azul-verdosos con detalle
natural del iris, pequeña marca de nacimiento en mejilla izquierda, arete
de aro delgado dorado, cabello castaño oscuro de largo medio con ondas
naturales, rasgos faciales suaves con ligera asimetria natural, textura de
piel natural sutil, expresion serena y cercana.
"""

REFERENCE_IMAGE_PATH = Path("virtual-character/output/_lyra_referencia.png")

ESCENAS = {
    "yoga_studio_mañana": (
        "de cuerpo completo, de pie en un estudio de yoga, ropa deportiva "
        "beige/crema, piso de madera, ventana grande con luz natural de "
        "mañana, paredes blancas, plantas verdes de fondo, sonrisa suave, "
        "fotorrealista, iluminacion natural suave, esteticamente minimalista"
    ),
    "gym_entrenamiento": (
        "en un gimnasio moderno, ropa deportiva funcional, media accion de "
        "entrenamiento (ej. sosteniendo mancuernas o en plancha), expresion "
        "enfocada pero accesible, iluminacion de gimnasio realista"
    ),
    "lifestyle_casual": (
        "en un espacio exterior o cafe, ropa casual/athleisure, sosteniendo "
        "un batido o botella de agua, expresion relajada y natural, luz "
        "de dia natural"
    ),
    "cafe_manana": (
        "sentada en una mesa de cafe al aire libre, sosteniendo una taza de "
        "cafe, luz calida de mañana, sonrisa relajada y natural, ambiente "
        "urbano acogedor"
    ),
    "viaje_paisaje": (
        "de pie frente a un paisaje de montaña o costa, ropa casual de "
        "viaje, mochila pequeña, expresion de asombro tranquilo, luz "
        "natural de exterior, composicion tipo foto de viaje"
    ),
    "deporte_aire_libre": (
        "corriendo o caminando en un sendero natural al aire libre, ropa "
        "deportiva, expresion energica y motivada, luz natural de dia"
    ),
    "con_mascota": (
        "sentada en el pasto de un parque, acompañada de un perro pequeño "
        "o mediano, sonrisa calida genuina, luz natural de tarde, ambiente "
        "relajado y cotidiano"
    ),
}


def cargar_referencia():
    if REFERENCE_IMAGE_PATH.exists():
        return REFERENCE_IMAGE_PATH.read_bytes()
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--escena", choices=list(ESCENAS.keys()), required=True)
    parser.add_argument("--n", type=int, default=1, help="numero de variaciones")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"{LYRA_DESCRIPCION_BASE}\n\nEscena: {ESCENAS[args.escena]}\n\nEste es un personaje ficticio para un proyecto de contenido de bienestar/lifestyle generado por IA."

    referencia = cargar_referencia()
    contenido = [prompt]
    if referencia:
        contenido = [
            "Manten la identidad visual EXACTA de esta referencia (mismo "
            "rostro, tono de piel, cabello, ojos):",
            types.Part.from_bytes(data=referencia, mime_type="image/png"),
            prompt,
        ]

    out_dir = Path("virtual-character/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.n):
        response = generate_with_retry(client, model=MODELO_GRATIS, contents=contenido, modelo_respaldo=None)
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img_bytes = part.inline_data.data
                out_path = out_dir / f"{args.escena}_{i}.png"
                out_path.write_bytes(img_bytes)
                print(f"Imagen generada: {out_path}")

                # Guarda la primera imagen generada como referencia futura
                if not referencia and not REFERENCE_IMAGE_PATH.exists():
                    REFERENCE_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
                    REFERENCE_IMAGE_PATH.write_bytes(img_bytes)
                    print(f"Guardada como referencia de identidad: {REFERENCE_IMAGE_PATH}")


if __name__ == "__main__":
    main()
