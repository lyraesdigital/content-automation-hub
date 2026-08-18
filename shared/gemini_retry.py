"""
Helper compartido: reintenta llamadas a Gemini ante errores temporales
(503 alta demanda, 429 rate limit) con backoff exponencial, y cae a un
modelo de respaldo si el principal sigue saturado tras varios intentos.

Uso:
    from shared.gemini_retry import generate_with_retry

    response = generate_with_retry(client, model="gemini-flash-latest",
                                    contents=prompt, config=config)
"""
import time
from google.genai import errors as genai_errors

REINTENTABLES = (503, 429)
MODELO_RESPALDO = "gemini-flash-lite-latest"


def generate_with_retry(client, max_intentos=4, espera_inicial=10, **kwargs):
    modelo_original = kwargs.get("model")
    for intento in range(1, max_intentos + 1):
        try:
            return client.models.generate_content(**kwargs)
        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            codigo = getattr(e, "code", None) or getattr(e, "status_code", None)
            if codigo not in REINTENTABLES:
                raise
            if intento == max_intentos:
                raise
            # A mitad de los intentos, si seguimos fallando, probamos el
            # modelo de respaldo por si el problema es especifico del
            # modelo principal (saturacion puntual de un modelo nuevo).
            if intento == max_intentos - 1 and kwargs.get("model") == modelo_original:
                print(f"[fallback] {modelo_original} sigue saturado, "
                      f"probando {MODELO_RESPALDO}...")
                kwargs["model"] = MODELO_RESPALDO
            espera = espera_inicial * (2 ** (intento - 1))
            print(f"[reintento {intento}/{max_intentos}] {codigo} - "
                  f"esperando {espera}s antes de reintentar...")
            time.sleep(espera)
