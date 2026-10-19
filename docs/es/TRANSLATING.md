# Localización

> **Cómo entregar una traducción:** La [guía de tareas en español](CONTRIBUTION_WORKFLOW.md) es el procedimiento actual. Un responsable reserva las líneas; escribes en la hoja asignada y otra persona revisa antes de que el bot cree el PR. Los pasos de edición y envío manual de abajo quedan como referencia de formatos y mantenimiento; no sustituyen la reserva ni la aprobación.

_Esta página se tradujo con ayuda de IA. Si el español es tu lengua materna, ayúdanos a mejorarla con un pull request. La [versión en inglés](../../localization/README.md) es la referencia._

Los textos de la interfaz de Ebbtide, listos para traducir. El juego está escrito en coreano, y el inglés es la fuente de todos los demás idiomas. Las rutas de esta página parten de la carpeta [`localization/`](../../localization/).

## Carpetas

| Ruta | Qué contiene |
| --- | --- |
| `source/strings/<Table>.csv` | Texto actual del juego: `key`, `en`, `ko`. No lo edites; se vuelve a generar desde el juego. |
| `source/SNAPSHOT` | Fecha y tamaño de la instantánea actual del texto fuente |
| `translations/<lang>/<Table>.csv` | Una carpeta por idioma: `key`, `en`, `translation`, `status` |
| `glossary.csv` | Nombres y términos militares, y cómo tratarlos |

Las carpetas de idioma usan códigos como `de`, `fr`, `pt-BR`, `ro`, `zh-Hans`.

## Cómo traducir

1. Abre un [issue de traductor](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) para tu idioma. Un mantenedor crea la carpeta del idioma.
2. Edita los archivos de `translations/<lang>/`. Rellena solo la columna `translation`.
3. Deja cada marcador exactamente igual que en inglés: `{0}`, `{1}`, etiquetas de texto enriquecido como `<b>` y saltos de línea `\n`. Puedes moverlos dentro de la frase.
4. Consulta `glossary.csv` para los nombres y los términos.
5. Abre un pull request. Una comprobación automática avisa si faltan marcadores o si hay filas rotas.

Si tienes dudas, deja vacía la columna `translation` de esa fila; en el juego, una fila vacía se muestra en inglés.

### Editar archivos CSV

- El editor web de GitHub sirve para cambios pequeños.
- Para trabajos más grandes, usa LibreOffice Calc o Google Sheets. Importa como UTF-8 con la coma como separador, y vuelve a exportar a CSV en UTF-8 con las mismas cuatro columnas.
- Evita Microsoft Excel, salvo que guardes como "CSV UTF-8"; otros formatos rompen los caracteres que no son del inglés (como la ñ o las tildes).

## La columna `status`

| Valor | Significado | Qué hacer |
| --- | --- | --- |
| (vacío) | Está bien, o aún no se ha traducido | Tradúcela si está vacía |
| `outdated` | El texto en inglés cambió después de traducirse | Actualiza la traducción y luego borra el estado |
| `review` | Un revisor quiere volver a mirarla | Coméntalo en el pull request |

## Cuando cambia el texto del juego

El juego sigue en desarrollo, así que el texto en inglés se añade, cambia y elimina a menudo. Cuando se actualiza la fuente, un mantenedor ejecuta `python tools/l10n.py update`, que:

- añade filas nuevas con la traducción vacía,
- marca como `outdated` las filas cuyo inglés cambió, y conserva tu traducción anterior,
- elimina las filas que ya no existen en el juego.

## Para mantenedores

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

Las escenas de historia (diálogos de las cinemáticas) aún no están incluidas. Se añadirán cuando el guion sea definitivo.
