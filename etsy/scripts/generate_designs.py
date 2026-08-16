"""
Genera conceptos de diseno diferenciados (no generico tipo "wall art IA") mas
titulo, descripcion y tags optimizados para busqueda en Etsy.

NICHO: edítalo con el nicho que definas tras tu conversacion inicial con
clientes (el paso humano que ya tienes planeado).
"""
import os
import json
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

NICHO = "define aqui tu nicho tras hablar con clientes reales"

PROMPT_TEMPLATE = """
Eres disenador de producto para Etsy, especializado en: {nicho}

El mercado de "wall art" generico con IA esta saturado. Genera 3 conceptos de
diseno que se diferencien por: estilo visual especifico, uso practico distinto
al decorativo puro, o personalizacion real (no solo "puedes cambiar el texto").

Para cada concepto entrega:
- Descripcion visual concreta (para brief de diseno, no la imagen en si)
- Titulo optimizado para busqueda en Etsy (max 140 caracteres)
- 13 tags relevantes (formato lista, sin espacios en cada tag de mas de 20 caracteres)
- Descripcion de producto (2-3 frases, tono humano, no generico)

Devuelve SOLO un JSON: {{"conceptos": [{{"descripcion_visual": "...", "titulo": "...",
"tags": ["..."], "descripcion_producto": "..."}}]}}
"""


def main():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = PROMPT_TEMPLATE.format(nicho=NICHO)
    response = model.generate_content(prompt)
    raw = response.text.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)

    out_dir = Path("etsy/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "conceptos.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    print(f"Conceptos generados en {out_dir}/conceptos.json")


if __name__ == "__main__":
    main()
