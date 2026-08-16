# content-automation-hub

Monorepo con 4 pipelines de generación de contenido automatizados vía GitHub Actions.
Cada pipeline **genera contenido y abre un Pull Request para revisión** — nada se publica
sin que lo apruebes manualmente. Diseñado para encajar en 1h/día entre semana + fin de semana.

## Estructura

```
content-automation-hub/
├── .github/workflows/          ← los 4 workflows (uno por proyecto)
├── youtube-kids/scripts/       ← canal infantil educativo
├── virtual-character/scripts/  ← personaje virtual (dropshipping + Hotmart/Skool)
├── etsy/scripts/                ← diseños para Etsy
└── facebook-images/scripts/    ← imágenes para páginas de Facebook (motivación primero)
```

## Por qué un solo repo y no 4

- GitHub Actions es gratis y sin límite de minutos en repos públicos, así que separar en
  4 repos no ahorra nada.
- Un solo lugar para gestionar Secrets (tus API keys), en vez de configurarlas 4 veces.
- Si en algún momento quieres vender o traspasar UNO de los proyectos, ahí sí conviene
  moverlo a su propio repo — pero no antes.

## Cómo funciona el flujo de revisión (importante)

1. El workflow corre solo, según el cron programado (o lo lanzas tú a mano desde la pestaña
   "Actions" de GitHub — botón "Run workflow").
2. Genera el guion/imagen/contenido y lo deja en una rama nueva + abre un Pull Request.
3. Tú recibes notificación del PR, lo revisas en tu hora diaria (texto, guion, imagen —
   lo que corresponda), y si está bien, le das "Merge".
4. El merge es la señal de "aprobado" — desde ahí subes/publicas manualmente la primera
   temporada, y cuando confíes en la calidad, automatizamos también ese último paso.

## Setup inicial (una sola vez)

1. Crea el repo en GitHub (público) y sube esta carpeta.
2. Ve a Settings → Secrets and variables → Actions → añade estos secrets según lo que
   uses en cada proyecto:
   - `GEMINI_API_KEY` (guion — capa gratuita generosa)
   - `ANTHROPIC_API_KEY` (opcional, para guiones/narración de más calidad — de pago)
   - `PEXELS_API_KEY` (video/imágenes de stock — gratis)
   - Claves de imagen/voz que decidas añadir más adelante
3. Revisa el cron de cada workflow (`.github/workflows/*.yml`) y ajústalo a tu ritmo real.
4. El primer mes, deja todos los cron en modo "manual" (`workflow_dispatch` sin schedule)
   hasta que confíes en la calidad — luego activas el schedule.

## Herramientas gratuitas usadas en los scripts

- **Guion**: Gemini (capa gratuita) para volumen; Claude para piezas que se locutan
  directamente y donde la calidad del texto importa más.
- **Voz**: edge-tts (gratis, sin API key).
- **Video/imagen de stock**: Pexels API (gratis).
- **Edición**: FFmpeg (gratis, viene preinstalado en los runners de GitHub Actions).

Nota: las claves de las capas gratuitas cambian de condiciones con frecuencia — verifica
los límites actuales en el dashboard de cada proveedor antes de escalar el volumen.
