# Tareas de traducción

Esta guía se ha traducido con ayuda de IA. La [versión inglesa](../CONTRIBUTION_WORKFLOW.md) es la referencia. Si dominas el español, tus correcciones de redacción son bienvenidas; esta versión no se presenta como revisada por una persona nativa.

Google Sheets sirve para escribir y revisar las traducciones. Un issue de trabajo en GitHub reserva las líneas, identifica a las personas responsables y controla cuándo una copia revisada se convierte en un pull request (PR).

**Editar la hoja no actualiza el repositorio ni el juego.** El bot lleva una copia exacta y revisada a un PR. Un responsable del repositorio revisa y fusiona ese PR, y el desarrollador incorpora el resultado a una versión del juego.

Este proceso cubre textos de interfaz existentes (`ui`) y traducciones escritas de guiones de voz (`voice-text`). Las grabaciones, audiciones, diálogos nuevos y textos sin ID de origen siguen su propio proceso de preparación. Publicar esta guía no asigna ninguna tarea: espera la confirmación del bot antes de empezar.

Las traducciones de la comunidad se entregan mediante el PR que crea el bot. Abrir un PR de traducción manualmente no permite saltarse la reserva ni la aprobación de la copia revisada.

## Quién hace cada cosa

| Persona | Responsabilidad |
| --- | --- |
| Traductor (`Contributor`) | Escribe la traducción asignada en la hoja y solicita una vista previa. |
| Revisor (`Reviewer`) | Revisa el contexto, la terminología, la naturalidad y la copia exacta. Aprueba su hash con su propia cuenta de GitHub. |
| Responsable del repositorio | Prepara o comprueba la tarea, reserva las líneas, gestiona el acceso a la hoja y revisa y fusiona el PR. |

El traductor y el revisor deben ser **usuarios distintos de GitHub**. El bot comprueba la identidad y la estructura de los archivos; la calidad de la traducción la revisan personas.

Puedes traducir enteramente en Google Sheets, sin instalar Git, clonar el repositorio ni crear tu propio PR. La persona que aprueba la vista previa necesita una cuenta de GitHub. Si necesitas ayuda para publicar el comentario que solicita la vista previa, un responsable puede hacerlo por ti.

## 1. Acordar una tarea pequeña

Solicita participar mediante el issue de traductor existente o un ticket de soporte en Discord. Antes de empezar, un responsable acuerda el idioma, el traductor, el revisor y las líneas asignadas.

La hoja privada de candidatos solo sirve para gestionar solicitudes. No es el registro de reservas y su contenido no debe copiarse a issues públicos.

Abre un issue con el formulario [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Conserva estos nombres de campo:

| Campo | Qué introducir |
| --- | --- |
| Kind | `ui` o `voice-text` |
| Locale | Código de idioma del repositorio, por ejemplo `ja`, `ru` o `pt-BR` |
| Table or voice role | Nombre de una tabla o papel de voz existente, sin ruta ni extensión `.csv` |
| Contributor | Un nombre de usuario de GitHub, sin `@` |
| Reviewer | El nombre de otro usuario de GitHub, sin `@` |
| Spreadsheet URL | Enlace al archivo de Google Sheets que se usará |
| Sheet tab | Nombre exacto de la pestaña de la hoja |
| First key | Primera clave existente que se incluirá |
| Last key | Última clave existente que se incluirá |

El intervalo incluye **ambos extremos en el orden del archivo de origen del repositorio**; no sigue el orden alfabético ni el orden actual de la hoja. El máximo es de **200 claves**. Para los guiones de voz, la clave es el identificador `file`, sin `.wav` ni `.flac`.

Cada tarea abarca un solo idioma y una sola tabla de interfaz o papel de voz. Los intervalos pequeños son más fáciles de revisar y generan menos conflictos cuando cambia el juego.

## 2. Reservar antes de traducir

Un responsable publica este comentario en el issue:

```text
/work assign
```

Espera a que el bot confirme la reserva. Rellenar o cerrar un issue, o escribir un nombre en una hoja, no reserva ni libera el trabajo.

El bot guarda la asignación en `registry.json`, en la rama `community-work-state`. Fija los campos del issue, las claves exactas y el hash del origen. Rechaza solapamientos con otras tareas activas del mismo tipo, idioma y tabla o papel de voz. Idiomas distintos pueden trabajar sobre las mismas claves.

Editar después el cuerpo del issue no modifica la asignación. Si cambian las líneas, la hoja, el traductor o el revisor, pide a un responsable que libere la tarea y cree una nueva reserva corregida.

## 3. Trabajar en la hoja

Un responsable proporciona las filas de origen actuales y concede permiso de edición a las personas asignadas. El bot debe poder leer el archivo sin iniciar sesión en Google, pero la edición debe estar limitada a quienes trabajan en él.

Protege las claves y el texto inglés. Los participantes solo deben editar las celdas necesarias. No actives «Cualquier persona con el enlace puede editar». Los permisos y los rangos protegidos se configuran manualmente; el bot de GitHub no administra los permisos de Google.

Para interfaz, conserva estas cuatro columnas CSV:

```text
key,en,translation,status
```

La pestaña debe contener filas de **una sola tabla**, la indicada en la tarea. La lista maestra que combina varias tablas sirve de referencia, pero no se puede importar directamente como pestaña de trabajo. El bot comprueba todas las filas con contenido de la pestaña frente a esa tabla de origen.

Edita `translation` y utiliza los valores de `status` existentes. Para importar una fila de interfaz, `status` debe estar **vacío**. `review` y `outdated` bloquean esa fila. Dejar el estado vacío no equivale a aprobar: sigue siendo necesaria la revisión independiente.

Para traducir guiones de voz, conserva estos encabezados exactos y en este orden:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Las pestañas actuales de japonés, ruso y coreano usan este formato. El bot filtra por el valor exacto de `Role`, como `carrier_jet_pilot`, y selecciona las claves reservadas de `Take file`. Rellena `Translation` y marca las filas revisadas como `Approved` en `Review status`.

El texto aprobado se guarda en `voice/translations/<locale>/<role>.csv`, con las columnas `key,en,translation,status`. Solo se importa **texto escrito**: esto no aprueba una grabación ni confirma que una línea provisional esté implementada en el juego.

En ambos tipos de tarea:

- Conserva los marcadores de posición, las etiquetas necesarias y los códigos de salto de línea.
- Mantén las claves y el inglés idénticos al origen asignado.
- Completa todas las traducciones del intervalo antes de solicitar la vista previa.
- Trata las celdas como texto. No uses fórmulas para obtener o generar traducciones.
- No incluyas datos de contacto privados, mensajes de tickets ni audiciones en la hoja o en el issue público.

Si no puedes terminar una tarea, acuerda dividirla o liberarla con un responsable, en lugar de mantener indefinidamente una reserva a medias.

## 4. Solicitar y revisar la vista previa

El traductor asignado, el revisor asignado o un responsable comenta:

```text
/work preview
```

El bot lee el intervalo reservado mediante la exportación CSV pública de Google Sheets. Comprueba el origen fijado, los estados, que las traducciones no estén vacías y las variables necesarias. También comprueba la traducción actual del repositorio para detectar cambios de otras personas antes de aprobar.

El bot guarda una copia inmutable y publica su hash SHA-256 con un enlace para revisarla. Revisa **esa copia**, no solo el resumen del issue o la hoja en directo. La hoja puede cambiar después de generar la vista previa.

El revisor comprueba:

- El significado y el contexto respecto al inglés.
- La naturalidad y la coherencia con el glosario.
- La longitud en pantalla o la forma de decir la frase, según corresponda.
- La posición de variables, etiquetas y saltos de línea.

Si hay que cambiar algo, edita la hoja y ejecuta `/work preview` otra vez. Usa el hash nuevo. El enlace de la vista previa sirve para revisar; no autoriza la fusión.

## 5. Aprobar la copia exacta

**Solo el revisor asignado** publica este comentario, sustituyendo `<sha256>` por el hash completo de la vista previa:

Publica los comandos como comentarios en el issue de trabajo de GitHub que se te haya asignado. Para aprobar, copia los 64 caracteres que aparecen después de `Digest:` en la respuesta del bot a la vista previa y sustituye solo `<sha256>` en el ejemplo; conserva el comando en inglés y no envíes literalmente ese marcador.

```text
/work approve <sha256>
```

El bot verifica quién aprueba, vuelve a leer la hoja y exige que coincida con la copia revisada. También comprueba que no hayan cambiado el origen ni el archivo de destino del repositorio. Un cambio en la hoja o el destino requiere otra vista previa. Un cambio en la tabla de origen requiere una nueva asignación, como se explica más abajo.

Si todo es correcto, el bot abre un PR con los archivos validados. **No lo fusiona.** El valor `Approved` de la hoja o un comentario como «está bien» no sustituyen este comando.

Un responsable revisa los cambios y fusiona el PR cuando pasan las comprobaciones. Hasta entonces, el trabajo sigue reservado. Los comentarios sobre los archivos propuestos se mantienen en ese PR.

La política de confianza `reviewed-sheet` compara el PR con su reserva y la copia aprobada. Lee los archivos del PR como datos y ejecuta código de la rama predeterminada de confianza. Rechaza PR de traducción manuales, archivos modificados después de aprobar y archivos adicionales incluidos en la entrega. Editar una rama del bot no permite sustituir el texto aprobado.

## 6. Terminar o liberar la reserva

Cuando el PR se fusione o se cierre, un responsable ejecuta:

```text
/work sync
```

Un PR fusionado completa la tarea; uno cerrado sin fusionar libera la reserva. Comprueba la confirmación del bot: el estado del issue no cambia por sí solo el registro.

El coordinador también sincroniza automáticamente los PR registrados del bot al recibir el evento de cierre de GitHub. Usa `/work sync` si esa ejecución no termina. En un PR abierto, el mismo comando vuelve a solicitar las comprobaciones, por ejemplo si falló su lanzamiento tras crear el PR.

Para cancelar una asignación antes de que exista un PR, un responsable comenta:

```text
/work release
```

Si hay un PR abierto, hay que cerrarlo antes de liberar la reserva. Así no habrá dos entregas activas para el mismo intervalo.

## Referencia de comandos

| Comando | Quién puede usarlo | Resultado |
| --- | --- | --- |
| `/work assign` | Responsable | Fija la tarea y reserva las claves. |
| `/work preview` | Traductor asignado, revisor asignado o responsable | Valida y guarda una copia para revisar. |
| `/work approve <sha256>` | Revisor asignado | Vuelve a comprobar esa copia y abre un PR. |
| `/work release` | Responsable | Cancela la reserva si no hay un PR abierto. |
| `/work sync` | Responsable | Sincroniza el estado del PR y el registro; si sigue abierto, solicita otra vez sus comprobaciones. |

## Cuando cambia el texto del juego

No crees un archivo de Google Sheets nuevo para cada versión del juego. Las claves estables permiten conservar traducciones cuando se actualiza el origen. Añade filas mediante el proceso de actualización del repositorio y marca los textos modificados para revisar, como explica [Localización](../../localization/README.md).

La asignación fija una copia de **toda la tabla de interfaz o del papel de voz**. Si cambia esa tabla antes de aprobar, la importación se detiene, aunque no hayan cambiado las claves reservadas. Un responsable cierra cualquier PR de entrega abierto, libera la tarea anterior, actualiza el origen de la hoja y abre **un issue de trabajo nuevo**. Conserva la traducción ya hecha y compárala con el origen actualizado; después el revisor comprueba una vista previa nueva. Las tareas de otras tablas pueden continuar.

Una fila de planificación sin ID de origen real no se puede importar. Déjala en planificación hasta que el desarrollador añada la entrada de origen. No inventes IDs de producción ni subas una hoja completa para incluir contenido futuro.

## Configuración y límites para responsables

Activa el proceso solo cuando su código y el formulario estén fusionados en la rama predeterminada. El registro está en `community-work-state`; no lo edites manualmente mientras se procesan comandos.

Se usa el `GITHUB_TOKEN` del repositorio con permisos para escribir el estado y la rama del bot, comentar en issues y crear PR. No hace falta conectar Google OAuth ni usar un token de acceso personal. El acceso a Google se limita a leer el CSV público.

En los ajustes de Actions del repositorio, permite que GitHub Actions cree PR. La identidad del bot debe seguir separada de la persona que revisa el idioma.

No dependas de que un PR del bot active automáticamente los procesos `pull_request`. El importador valida los archivos y lanza explícitamente `check.yml` para la rama del bot y `delivery-policy.yml` desde la rama predeterminada de confianza para ese número de PR.

Protege la rama predeterminada exigiendo `check` y el estado de commit `reviewed-sheet`. El proceso de política necesita permiso para publicar ese estado. Verifica ambos antes de fusionar: añadir los archivos del proceso no configura por sí solo la protección de ramas.

El registro evita asignaciones solapadas y la política obligatoria impide saltárselas con PR manuales. Ninguno gestiona los permisos de Google Sheets: limita la edición y protege el origen.

Las comprobaciones automáticas detectan fallos de estructura y contenido desactualizado. Las personas siguen siendo responsables de la calidad, el contexto, las condiciones de participación y la adecuación al juego.
