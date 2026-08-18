"""
Genera conceptos de imagen + copy para pagina de Facebook, segun nicho.

Uso: python generate_images.py --niche motivacion
     python generate_images.py --niche religion   (tratar como secundario,
     ver README/notas del proyecto sobre techo de monetizacion mas bajo)
     python generate_images.py --niche tarot       (idem)
"""
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

PROMPT_TEMPLATE = """
Eres creador de contenido para una pagina de Facebook de nicho: {nicho}

Genera 3 conceptos de imagen (formato reel/post) pensados para retencion y
para compartir. Para cada uno entrega:
- Concepto visual (brief para generar la imagen)
- Texto corto superpuesto (max 12 palabras, alto impacto)
- Copy del post (2-3 frases)
- Por que crees que generaria retencion/compartidos en este nicho especifico

Devuelve SOLO un JSON: {{"nicho": "{nicho}", "conceptos": [{{"concepto_visual": "...",
"texto_imagen": "...", "copy_post": "...", "razon_retencion": "..."}}]}}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--niche", required=True, choices=["motivacion", "religion", "tarot"])
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = PROMPT_TEMPLATE.format(nicho=args.niche)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    raw = response.text.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)

    out_dir = Path("facebook-images/output") / f"{args.niche}_{datetime.utcnow().strftime('%Y-%m-%d_%H%M')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "conceptos.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    print(f"Conceptos generados en {out_dir}/conceptos.json — nicho: {args.niche}")


if __name__ == "__main__":
    main()
