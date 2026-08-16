"""
Convierte el guion en audio usando edge-tts (gratuito, sin API key).
Busca la carpeta de salida mas reciente creada por generate_script.py.
"""
import json
import asyncio
from pathlib import Path

import edge_tts

# Voz en espanol, calida, apta para narracion infantil.
VOZ = "es-MX-DaliaNeural"


def carpeta_mas_reciente():
    base = Path("youtube-kids/output")
    carpetas = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime)
    return carpetas[-1]


async def generar_audio(texto: str, salida: Path):
    comunicador = edge_tts.Communicate(texto, VOZ)
    await comunicador.save(str(salida))


def main():
    out_dir = carpeta_mas_reciente()
    data = json.loads((out_dir / "script.json").read_text())

    texto_completo = f"{data['guion']} {data['moraleja']}"
    salida = out_dir / "voz.mp3"

    asyncio.run(generar_audio(texto_completo, salida))
    print(f"Audio generado en {salida}")


if __name__ == "__main__":
    main()
