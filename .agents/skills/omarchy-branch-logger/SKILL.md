---
name: omarchy-branch-logger
description: >-
  Create a dedicated Git branch and Markdown record on GitHub for each Omarchy issue, bug fix, or requested feature.
  Summarizes problems, root causes, and final solutions in a structured, concise Markdown file, pushes the branch to GitHub (@dagudelob/omarchy-setup), and maintains a clean catalog in the main branch.
  Use whenever the user asks to document an issue/fix/feature, save a resolution to a branch, create a branch for a problem, or triggers phrases like "crear rama para este problema", "guardar solucion en una rama", "documentar este arreglo", "registrar feature", "bitacora de soluciones".
---

# Omarchy Branch Logger Skill

Organizes, documents, and pushes every troubleshooting fix or feature into its own isolated Git branch in GitHub (`@dagudelob/omarchy-setup`), keeping solutions clean, searchable, and structured with concise Markdown records.

## Objetivo
Evitar el desorden de mezclar múltiples soluciones o notas en una sola rama. Cada problema o mejora tiene:
1. Su propia rama (`fix/<slug>` o `feature/<slug>`).
2. Un archivo Markdown super resumido con: problema, causa raíz, solución final paso a paso, archivos tocados y validación.
3. Actualización automática de la tabla/catálogo `RESOLUTIONS.md` en la rama `main` con enlaces directos a cada rama en GitHub.

---

## Repositorio
- **Directorio local:** `/home/dagudelo/Code/omarchy-setup`
- **GitHub:** `https://github.com/dagudelob/omarchy-setup`

---

## Procedimiento Paso a Paso para el Agente

Cuando el usuario pida documentar un inconveniente, registrar una solución o crear una rama:

### Paso 1: Identificar el Tipo y Nombre de la Rama
- Determinar el tipo: `fix` (inconveniente / error / corrección) o `feature` (nueva funcionalidad / configuración nueva).
- Generar un slug descriptivo en minúsculas y kebab-case (ej. `omarchy-update-path-mismatch`, `surface-touch-support`, `hyprland-multi-monitor`).

### Paso 2: Crear y Activar la Rama
Ejecuta el script helper para inicializar la rama y la plantilla Markdown:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/log-solution.sh <fix|feature> <slug> "<Título descriptivo del arreglo>"
```

Esto generará el archivo `docs/resolutions/YYYY-MM-DD-<slug>.md` en la nueva rama.

### Paso 3: Redactar el Resumen Ejecutivo en el Markdown
Edita el archivo generado `docs/resolutions/YYYY-MM-DD-<slug>.md` asegurando que sea **supremamente resumido, conciso y directo**:

```markdown
# [Título del Arreglo / Feature]

- **Fecha:** YYYY-MM-DD
- **Rama:** `fix/<slug>` o `feature/<slug>`
- **Tipo:** `fix` | `feature`

---

## 1. Inconveniente / Requerimiento
Breve resumen de 2-3 líneas explicando el síntoma, el mensaje de error exacto o la necesidad.

## 2. Causa Raíz
Explicación técnica en 1-2 líneas de qué causaba el comportamiento.

## 3. Solución Aplicada
Comandos exactos ejecutados y pasos definitivos aplicados. Código o snippets clave.

## 4. Archivos Modificados
- `~/.config/...`: Breve descripción del cambio.
- `/usr/...` (si aplica): Breve descripción.

## 5. Validación
Prueba realizada para confirmar que el problema quedó resuelto.
```

*(Si la solución implicó modificar archivos de dotfiles que ya son respaldados por el repo, asegúrate de que también queden reflejados en la carpeta `config/` de la rama).*

### Paso 4: Publicar la Rama en GitHub y Actualizar el Catálogo
Ejecuta el script de publicación:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/publish-solution.sh "docs: registrar solucion para <slug>"
```

Este script:
1. Aplica el escaneo de seguridad contra secretos y tokens (`ghp_`, `BEGIN PRIVATE KEY`).
2. Confirma y sube la rama a GitHub: `git push -u origin <branch>`.
3. Vuelve a la rama `main` y añade una entrada al archivo `RESOLUTIONS.md` con enlace a la rama en GitHub.
4. Sube la actualización de `main` a GitHub.

### Paso 5: Confirmar al Usuario
Informa al usuario con:
- El nombre de la rama creada.
- El resumen ultracompacto de la solución.
- El enlace directo a la rama en GitHub: `https://github.com/dagudelob/omarchy-setup/tree/<branch>`.
- El enlace al catálogo general: `https://github.com/dagudelob/omarchy-setup/blob/main/RESOLUTIONS.md`.
