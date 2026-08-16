"""
Investiga tendencias de temporada relevantes para tu ubicacion (Espana) usando
Google Trends (via pytrends, gratis). Guarda un ranking simple para que el
paso de generacion de contenido lo use como input.

Idea: ajustar SEMILLAS segun la epoca del ano (esto es un punto de partida,
conviene revisarlo/ampliarlo cada 1-2 meses segun que funcione).
"""
import json
from datetime import datetime
from pathlib import Path

from pytrends.request import TrendReq

SEMILLAS = [
    "regalos otono", "decoracion hogar", "accesorios movil",
    "organizacion casa", "regalos originales", "fitness en casa",
]


def main():
    pytrends = TrendReq(hl="es-ES", tz=60)
    resultados = []

    for termino in SEMILLAS:
        pytrends.build_payload([termino], geo="ES", timeframe="now 7-d")
        related = pytrends.related_queries().get(termino, {})
        top = related.get("rising")
        if top is not None and not top.empty:
            for _, fila in top.head(3).iterrows():
                resultados.append({"semilla": termino, "tendencia": fila["query"], "valor": int(fila["value"])})

    resultados.sort(key=lambda x: x["valor"], reverse=True)

    out_dir = Path("virtual-character/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tendencias.json").write_text(json.dumps(resultados[:10], ensure_ascii=False, indent=2))

    print(f"Tendencias guardadas en {out_dir}/tendencias.json")


if __name__ == "__main__":
    main()
