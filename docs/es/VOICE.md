# Voz

> **Traducción escrita de guiones:** Usa la [guía de tareas en español](CONTRIBUTION_WORKFLOW.md). Necesitas líneas asignadas y un revisor distinto del traductor; trabajas en la hoja asignada y el bot crea el PR. Ese proceso importa texto, no grabaciones. Las instrucciones de audición, archivos de audio y formato de abajo siguen correspondiendo a la participación como actor de voz.

_Esta página se tradujo con ayuda de IA. Si el español es tu lengua materna, ayúdanos a mejorarla con un pull request. La [versión en inglés](../../voice/README.md) es la referencia._

Ahora mismo, todas las líneas de voz de Ebbtide están hechas con IA, y todas se van a reemplazar por actores de voz reales: pilotos, tripulaciones de helicóptero, oficiales de barco, tripulaciones de vehículos y escuadras de infantería. Las rutas de esta página parten de la carpeta [`voice/`](../../voice/).

## Cómo funciona

1. **Audición.** Publica una toma corta en el canal de envíos (submissions) de Discord, leyendo las frases de muestra que están fijadas allí.
2. **Casting.** Si tu voz encaja con un papel, un mantenedor se pone en contacto contigo y abre un ticket privado.
3. **Guion.** El guion completo de tu papel se añade a `scripts/<role>.csv`: nombre de archivo, situación, tono y línea.
4. **Entrega.** Abre un pull request que añada tus tomas a `takes/<role>/<your name>/`, un archivo por línea, con el nombre exacto que aparece en el guion.
5. **Revisión.** Escuchamos, pedimos repeticiones si hace falta, fusionamos y llevamos las líneas a la siguiente build.

## Especificaciones de grabación

Graba limpio y en seco; el juego ya añade por su cuenta los efectos de radio.

- Mejor FLAC (ocupa menos), o WAV. Mono, 48 kHz, 24 bits (44.1 kHz / 16 bits también vale).
- Sin reverberación, efectos, música ni filtro de radio.
- Una habitación silenciosa, sin eco ni ruido de fondo.
- Picos más altos en torno a -3 dB, sin llegar nunca a saturar (clipping).
- Una línea por archivo, con más o menos medio segundo de silencio antes y después.

## Antes de enviar nada

Lee [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) (está en inglés; el texto en inglés es la versión oficial), sobre todo la parte sobre grabaciones de voz. Si tienes menos de 18 años, tu padre, madre o tutor legal también tiene que aceptarlos contigo.
