"""
Genera el guion de un video educativo animado para niños.
Usa Gemini (capa gratuita) para volumen. Si prefieres calidad de narración
superior en piezas clave, sustituye por la API de Anthropic (de pago).

Salida: youtube-kids/output/<fecha>/script.json
"""
import os
import json
import random
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

# Rota entre temas de valores/aprendizaje para que no se repita siempre lo mismo.
TEMAS = [
    "companerismo: ayudar a un amigo que se siente excluido",
    "honestidad: admitir un error sin miedo",
    "paciencia: esperar el turno para jugar",
    "gratitud: decir gracias y notar el esfuerzo de otros",
    "trabajo en equipo: resolver un problema entre varios",
    "respeto por las diferencias: un amigo que hace las cosas distinto",
]

PROMPT_TEMPLATE = """
Eres guionista de contenido educativo infantil (edad 4-8 anos), estilo animado,
en espanol. Escribe un guion corto (60-90 segundos al narrarlo) sobre: {tema}

Estructura obligatoria:
1. Situacion inicial sencilla y reconocible para un nino.
2. Un pequeno conflicto o duda.
3. Como el personaje principal resuelve el conflicto (mostrando el valor, no
   explicandolo con un sermon).
4. Cierre breve con la moraleja dicha de forma natural, sin sonar a leccion.

Reglas:
- Frases cortas, vocabulario simple, tono calido.
- Nada de humor adulto, ironia o referencias que un nino no entienda.
- Sin nombres de marcas ni personajes con copyright.

Devuelve SOLO un JSON con este formato, sin texto adicional:
{{"titulo": "...", "tema": "{tema}", "guion": "...", "moraleja": "..."}}
"""


def main():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-3-flash")  # capa gratuita

    tema = random.choice(TEMAS)
    prompt = PROMPT_TEMPLATE.format(tema=tema)
    response = model.generate_content(prompt)

    # Limpieza básica por si el modelo envuelve el JSON en markdown.
    raw = response.text.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)

    out_dir = Path("youtube-kids/output") / datetime.utcnow().strftime("%Y-%m-%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "script.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    print(f"Guion generado en {out_dir}/script.json — tema: {tema}")


if __name__ == "__main__":
    main()
