"""
Helper compartido: reintenta llamadas a Gemini ante errores temporales
(503 alta demanda, 429 rate limit) con backoff exponencial.

Uso:
    from shared.gemini_retry import generate_with_retry

    response = generate_with_retry(client, model="gemini-flash-latest",
                                    contents=prompt, config=config)
"""
import time
from google.genai import errors as genai_errors

REINTENTABLES = (503, 429)


def generate_with_retry(client, max_intentos=4, espera_inicial=10, **kwargs):
    for intento in range(1, max_intentos + 1):
        try:
            return client.models.generate_content(**kwargs)
        except genai_errors.ServerError as e:
            codigo = getattr(e, "code", None) or getattr(e, "status_code", None)
            if codigo in REINTENTABLES and intento < max_intentos:
                espera = espera_inicial * (2 ** (intento - 1))
                print(f"[reintento {intento}/{max_intentos}] {codigo} - "
                      f"esperando {espera}s antes de reintentar...")
                time.sleep(espera)
                continue
            raise
        except genai_errors.ClientError as e:
            codigo = getattr(e, "code", None) or getattr(e, "status_code", None)
            if codigo in REINTENTABLES and intento < max_intentos:
                espera = espera_inicial * (2 ** (intento - 1))
                print(f"[reintento {intento}/{max_intentos}] {codigo} - "
                      f"esperando {espera}s antes de reintentar...")
                time.sleep(espera)
                continue
            raise
