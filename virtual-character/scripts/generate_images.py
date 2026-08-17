"""
Genera imagenes del personaje virtual (Lyra) usando Nano Banana Pro
(gemini-3-pro-image) via la misma GEMINI_API_KEY que ya usas para texto.

IMPORTANTE - LEE ANTES DE CORRER:
1. Generacion de imagenes NO tiene capa gratuita. Necesitas facturacion
   activa en el proyecto de Google Cloud asociado a tu API key.
2. Configura un presupuesto en Google Cloud Console (Billing > Budgets &
   alerts) ANTES de correr esto en volumen - igual que hicimos en GitHub.
3. Costo aproximado: ~$0.13 por imagen en resolucion 1K-2K (precios ago 2026,
   verifica en https://ai.google.dev/gemini-api/docs/pricing antes de escalar).
4. Este script mantiene consistencia del personaje pasando la PRIMERA imagen
   generada como referencia en las siguientes corridas (hasta 14 imagenes de
   referencia soporta el modelo).

Uso:
    python generate_images.py --escena "yoga_studio_mañana"
    python generate_images.py --escena "gym_entrenamiento" --n 3
"""
import os
import json
import base64
import argparse
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

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

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-3-pro-image")

    prompt = f"{LYRA_DESCRIPCION_BASE}\n\nEscena: {ESCENAS[args.escena]}\n\nEste es un personaje ficticio para un proyecto de contenido de bienestar generado por IA."

    referencia = cargar_referencia()
    contenido = [prompt]
    if referencia:
        contenido = [
            "Manten la identidad visual EXACTA de esta referencia (mismo "
            "rostro, tono de piel, cabello, ojos):",
            {"mime_type": "image/png", "data": referencia},
            prompt,
        ]

    out_dir = Path("virtual-character/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.n):
        response = model.generate_content(contenido)
        for part in response.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                img_bytes = base64.b64decode(part.inline_data.data) if isinstance(part.inline_data.data, str) else part.inline_data.data
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
