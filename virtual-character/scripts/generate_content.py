"""
Toma la tendencia mejor puntuada del paso anterior y genera un borrador de
contenido (post + guion corto) en la voz de tu personaje virtual.

IMPORTANTE: PERSONAJE_BIO es lo que define la consistencia de marca. Edítalo
UNA vez con la personalidad real de tu personaje y no lo cambies cada run —
la consistencia es lo que construye reconocimiento.
"""
import os
import json
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

PERSONAJE_BIO = """
Nombre: Lyra
Tono: cercana, serena, directa; wellness sin ser predicadora - habla como una
amiga que sabe de fitness y bienestar, no como coach de venta agresiva
Valores que transmite: equilibrio, constancia sobre perfeccion, practicidad,
honestidad sobre lo que recomienda (nada de superlativos vacios)
Publico objetivo: personas de 25 a 35 anos interesadas en vida fitness y
bienestar, que buscan contenido genuino mas que motivacion generica
Nicho de monetizacion: contenido + ebooks propios de fitness/bienestar,
recomendaciones de producto ocasionales (no cada post)
Identidad: personaje virtual generado por IA - se identifica como tal en su
bio/perfil, no se presenta como persona real
"""

PROMPT_TEMPLATE = """
Eres {personaje}

Basandote en esta tendencia de producto detectada: "{tendencia}"

Escribe:
1. Un post corto (para red social) presentando el producto de forma autentica,
   sin sonar a anuncio generico.
2. Un guion de 30-45 segundos para un video corto del personaje hablando de ello.

Reglas: nada de superlativos vacios ("el mejor", "increible"), habla como una
persona real recomendando algo a un amigo, no como un vendedor.

Devuelve SOLO un JSON: {{"post": "...", "guion_video": "..."}}
"""


def carpeta_mas_reciente():
    base = Path("virtual-character/output")
    carpetas = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime)
    return carpetas[-1]


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    out_dir = carpeta_mas_reciente()
    tendencias = json.loads((out_dir / "tendencias.json").read_text())
    top_tendencia = tendencias[0]["tendencia"] if tendencias else "producto de temporada"

    prompt = PROMPT_TEMPLATE.format(personaje=PERSONAJE_BIO, tendencia=top_tendencia)
    response = client.models.generate_content(
        model="gemini-3-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    raw = response.text.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)
    data["tendencia_usada"] = top_tendencia

    (out_dir / "contenido.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Contenido generado en {out_dir}/contenido.json — producto: {top_tendencia}")


if __name__ == "__main__":
    main()
