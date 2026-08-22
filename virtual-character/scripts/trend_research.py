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

# Fallback si Google Trends/pytrends falla (es una libreria no oficial y
# rompe con frecuencia por cambios de Google o rate-limit). Sin esto, todo
# el pipeline de Lyra se caia aunque el resto funcionara bien.
FALLBACK_TENDENCIAS = [
    {"semilla": "fitness en casa", "tendencia": "rutina de movilidad matutina", "valor": 50},
    {"semilla": "regalos originales", "tendencia": "regalo de bienestar personalizado", "valor": 50},
    {"semilla": "organizacion casa", "tendencia": "rutina de habitos saludables", "valor": 50},
]


def main():
    out_dir = Path("virtual-character/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        pytrends = TrendReq(hl="es-ES", tz=60)
        resultados = []

        for termino in SEMILLAS:
            pytrends.build_payload([termino], geo="ES", timeframe="now 7-d")
            related = pytrends.related_queries().get(termino, {})
            top = related.get("rising")
            if top is not None and not top.empty:
                for _, fila in top.head(3).iterrows():
                    resultados.append({"semilla": termino, "tendencia": fila["query"], "valor": int(fila["value"])})

        if not resultados:
            raise ValueError("pytrends no devolvio resultados")

        resultados.sort(key=lambda x: x["valor"], reverse=True)
        (out_dir / "tendencias.json").write_text(json.dumps(resultados[:10], ensure_ascii=False, indent=2))
        print(f"Tendencias guardadas en {out_dir}/tendencias.json")

    except Exception as e:
        print(f"[aviso] pytrends fallo ({e}), usando lista de respaldo")
        (out_dir / "tendencias.json").write_text(json.dumps(FALLBACK_TENDENCIAS, ensure_ascii=False, indent=2))
        print(f"Tendencias de respaldo guardadas en {out_dir}/tendencias.json")


if __name__ == "__main__":
    main()
