"""
Genera imagenes de los disenos de Etsy a partir de los conceptos ya
aprobados en conceptos.json, usando Gemini 2.5 Flash Image ("Nano Banana"
base, NO la version "Pro") via la misma GEMINI_API_KEY.

IMPORTANTE:
- gemini-2.5-flash-image SI tiene capa gratuita real (sin facturacion),
  a diferencia de gemini-3-pro-image-preview que usamos para Lyra.
- Calidad menor a la version Pro, pero suficiente para validar conceptos
  antes de decidir si pagar por mejor calidad (Higgsfield, Nano Banana Pro).
- Limite generoso pero no infinito - si falla con error de cuota, es la
  senal de que hay que esperar al dia siguiente o pasar a un modelo pago.

Uso:
    python generate_images.py --conceptos etsy/output/2026-08-17_2123/tumbler-wraps/conceptos.json
"""
import os
import sys
import json
import argparse
from pathlib import Path

from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.gemini_retry import generate_with_retry

import time

MODELO_GRATIS = "gemini-2.5-flash-image"
PAUSA_ENTRE_IMAGENES = 25  # segundos - respeta el limite de rate del tier gratis


def carpeta_mas_reciente():
    base = Path("etsy/output")
    carpetas = sorted([d for d in base.iterdir() if d.is_dir()], reverse=True)
    if not carpetas:
        raise SystemExit("No hay ninguna corrida en etsy/output/ todavia.")
    return carpetas[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conceptos", help="ruta a un conceptos.json especifico (opcional)")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    if args.conceptos:
        rutas = [Path(args.conceptos)]
    else:
        run_dir = carpeta_mas_reciente()
        rutas = list(run_dir.glob("*/conceptos.json"))
        if not rutas:
            raise SystemExit(f"No se encontraron conceptos.json dentro de {run_dir}")
        print(f"Usando corrida mas reciente: {run_dir} ({len(rutas)} nichos)")

    for conceptos_path in rutas:
        procesar_nicho(client, conceptos_path)


def procesar_nicho(client, conceptos_path):
    data = json.loads(conceptos_path.read_text())

    out_dir = conceptos_path.parent / "imagenes"
    out_dir.mkdir(parents=True, exist_ok=True)

    conceptos = data if isinstance(data, list) else data.get("conceptos", [])

    for i, concepto in enumerate(conceptos):
        descripcion = concepto.get("descripcion_visual") or concepto.get("descripcion") or concepto.get("concepto") or str(concepto)
        prompt = (
            f"Diseno grafico para producto de venta: {descripcion}. "
            f"Estilo ilustracion limpia, colores vibrantes, sin texto "
            f"superpuesto, fondo transparente o blanco solido, apto para "
            f"impresion en sublimacion/DTF."
        )

        response = generate_with_retry(
            client,
            model=MODELO_GRATIS,
            contents=prompt,
            modelo_respaldo=None,
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                out_path = out_dir / f"concepto_{i}.png"
                out_path.write_bytes(part.inline_data.data)
                print(f"Imagen generada: {out_path}")

        if i < len(conceptos) - 1:
            time.sleep(PAUSA_ENTRE_IMAGENES)


if __name__ == "__main__":
    main()
