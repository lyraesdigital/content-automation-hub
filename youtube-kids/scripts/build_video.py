"""
Descarga clips de stock relacionados con el tema (Pexels, gratis) y los une
con el audio narrado usando FFmpeg. Salida: video.mp4 en la misma carpeta.

Nota: para contenido infantil animado de verdad (no solo stock+voz), este
paso es el punto donde luego conviene enchufar un motor de animacion/avatar
en vez de solo video de stock. Sirve como version 1 funcional.
"""
import json
import subprocess
from pathlib import Path

import requests

PEXELS_URL = "https://api.pexels.com/videos/search"


def carpeta_mas_reciente():
    base = Path("youtube-kids/output")
    carpetas = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime)
    return carpetas[-1]


def descargar_clip_stock(query: str, destino: Path, api_key: str):
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    r = requests.get(PEXELS_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    video_url = r.json()["videos"][0]["video_files"][0]["link"]

    video_data = requests.get(video_url, timeout=60).content
    destino.write_bytes(video_data)


def main():
    import os

    out_dir = carpeta_mas_reciente()
    data = json.loads((out_dir / "script.json").read_text())

    clip_path = out_dir / "clip.mp4"
    descargar_clip_stock(data["tema"].split(":")[0], clip_path, os.environ["PEXELS_API_KEY"])

    audio_path = out_dir / "voz.mp3"
    video_final = out_dir / "video.mp4"

    # Recorta/loopea el clip a la duracion del audio y lo combina.
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(clip_path),
        "-i", str(audio_path),
        "-shortest",
        "-c:v", "libx264", "-c:a", "aac",
        str(video_final),
    ]
    subprocess.run(cmd, check=True)
    print(f"Video generado en {video_final}")


if __name__ == "__main__":
    main()
