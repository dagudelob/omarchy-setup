---
name: omarchy-branch-logger
description: >-
  Create a dedicated Git branch and Markdown record on GitHub for each Omarchy issue, bug fix, or requested feature.
  PRIMARY TRIGGER: Triggers immediately whenever the user says "este tema quedó solucionado", "tema solucionado", "quedó solucionado", "guardar solucion", "crear rama para este problema", or asks to document an issue/fix/feature into a branch.
  Summarizes the problem, root cause, and final solution in a structured, ultra-concise Markdown file, pushes the branch to GitHub (@dagudelob/omarchy-setup), and maintains a clean catalog in the main branch.
---

# Omarchy Branch Logger Skill

Organizes, documents, and pushes every troubleshooting fix or feature into its own isolated Git branch in GitHub (`@dagudelob/omarchy-setup`), keeping solutions clean, searchable, and structured with concise Markdown records.

## Disparador Principal (Trigger)
**SIEMPRE activar este skill cuando el usuario diga:**
- `"este tema quedó solucionado"`
- `"tema solucionado"`
- `"quedó solucionado"`
- `"documentar este arreglo"`
- `"crear rama para esta solución"`

---

## Repositorio
- **Directorio local:** `/home/dagudelo/Code/omarchy-setup`
- **GitHub:** `https://github.com/dagudelob/omarchy-setup`

---

## Procedimiento Automatizado para el Agente

En el momento exacto en que el usuario diga *"este tema quedó solucionado"*:

### Paso 1: Identificar el Tema Tratado en la Conversación
- Identifica el problema o funcionalidad que se acaba de resolver en los turnos recientes de la conversación.
- Determina el tipo:
  - `fix/` para errores, bugs, incompatibilidades o reparaciones.
  - `feature/` para nuevas configuraciones, herramientas o personalizaciones.
- Genera un slug corto y representativo en kebab-case (ej. `fix/omarchy-update-path`, `feature/auto-backup-skill`).

### Paso 2: Crear y Activar la Rama
Ejecuta el script helper para inicializar la rama:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/log-solution.sh <fix|feature> <slug> "<Título descriptivo del arreglo>"
```

### Paso 3: Redactar el Resumen Ejecutivo en el Markdown
Edita el archivo generado en `docs/resolutions/YYYY-MM-DD-<slug>.md` asegurando que sea **supremamente resumido, conciso y directo**:

```markdown
# [Título del Arreglo / Feature]

- **Fecha:** YYYY-MM-DD
- **Rama:** `fix/<slug>` o `feature/<slug>`
- **Tipo:** `fix` | `feature`

---

## 1. Inconveniente / Requerimiento
Resumen ejecutivo de 2-3 líneas: cuál era el error o qué se necesitaba lograr.

## 2. Causa Raíz
Explicación técnica en 1-2 líneas de la causa del problema.

## 3. Solución Aplicada
Comandos exactos ejecutados, ajustes en archivos y pasos definitivos aplicados.

## 4. Archivos Modificados
- Lista de rutas absolutas de archivos creados o editados.

## 5. Validación
Cómo se confirmó que la solución funciona correctamente.
```

*(Si la solución implicó archivos de configuración en `~/.config/`, ejecuta también una sincronización de esos archivos en la rama si corresponde).*

### Paso 4: Escaneo de Seguridad y Publicación en GitHub
Ejecuta:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/publish-solution.sh "docs: registrar solucion para <slug>"
```

El script automáticamente:
1. Aplica el filtro anti-secretos (tokens `ghp_`, `gho_`, llaves privadas SSH/RSA).
2. Hace commit en la rama de la solución.
3. Sube la rama a GitHub: `git push -u origin <branch>`.
4. Vuelve a `main` y actualiza la tabla maestra `RESOLUTIONS.md` con el enlace directo a la rama en GitHub.
5. Sube la actualización de `main` a GitHub.

### Paso 5: Responder al Usuario
Muestra en el chat un resumen ultracompacto:
- Nombre de la rama creada en GitHub.
- Breve resumen de 3 líneas de la solución registrada.
- Enlace directo a la rama: `https://github.com/dagudelob/omarchy-setup/tree/<branch>`.
- Enlace al catálogo general: `https://github.com/dagudelob/omarchy-setup/blob/main/RESOLUTIONS.md`.
