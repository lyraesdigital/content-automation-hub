"""
Genera conceptos de diseno diferenciados (no generico tipo "wall art IA") mas
titulo, descripcion y tags optimizados para busqueda en Etsy.

NICHOS: lista de nichos a generar en cada corrida. Orden = prioridad.
Basado en investigacion de demanda Etsy 2026 (agosto 2026):
- tumbler wraps: mayor demanda especifica del momento, compradores recurrentes
  (compran para cada festividad/ocasion/equipo/estacion)
- mascotas: compradores muy fieles, mercado enorme (56M+ hogares con perro
  en EEUU), motivacion de compra emocional
- wall art botanico/abstracto: mercado mas grande y estable, pendiente de activar
"""
import os
import json
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

NICHOS = [
    "tumbler wraps (disenos full-wrap para vasos termicos 20oz/30oz/40oz "
    "estilo Stanley) para festividades, cumpleanos, ocupaciones, equipos "
    "deportivos y estaciones del ano",
    "diseños y regalos personalizados para duenos de mascotas (perros y "
    "gatos) - retratos estilizados, placas, ropa impresa",
    # "wall art botanico y abstracto para impresion en casa",  # activar despues
]

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


def slugify(text: str) -> str:
    return text.split(" (")[0].strip().lower().replace(" ", "-")[:40]


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    run_dir = Path("etsy/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    run_dir.mkdir(parents=True, exist_ok=True)

    for nicho in NICHOS:
        prompt = PROMPT_TEMPLATE.format(nicho=nicho)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        raw = response.text.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)

        out_dir = run_dir / slugify(nicho)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "conceptos.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

        print(f"[{slugify(nicho)}] Conceptos generados en {out_dir}/conceptos.json")


if __name__ == "__main__":
    main()
