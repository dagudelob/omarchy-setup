---
name: antigravity-conversations-backup
description: >-
  Crea copias de seguridad y restaura conversaciones, artefactos e índices de Antigravity en la Microsoft Surface.
  Emite alertas mandatorias y guía al usuario cuando va a formatear la Surface, cambiar de máquina o después de una reinstalación limpia de Omarchy.
  Triggers: "backup conversaciones", "respaldo conversaciones", "backup antigravity", "restaurar conversaciones", "formatear surface", "cambiar de surface", "recuperar conversaciones".
---

# Antigravity Conversations Backup & Restore Skill (Surface / Omarchy)

Esta skill gestiona la preservación total del historial de conversaciones, artefactos en `brain/`, índices SQLite y estado de Google Antigravity en Omarchy.

## 🚨 ALERTA MANDATORIA: Antes de formatear o cambiar de Surface

Cuando el usuario mencione que va a **formatear la Surface**, **reinstalar el sistema** o **cambiar de equipo**:

1. **Emitir advertencia inmediata:**
   > ⚠️ **ALERTA CRÍTICA ANTES DE FORMATEAR / CAMBIAR DE EQUIPO:**
   > Si formateas la unidad o cambias de Surface, **todas las conversaciones y artefactos de Antigravity se perderán** si no se resguardan fuera del disco local (`~/.gemini/antigravity/` se elimina con el formato).
   > Debes generar un backup y transferirlo a un medio externo (USB, disco externo o Google Drive vía `rclone`).

2. **Ejecutar el script de respaldo:**
   ```bash
   /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh backup --cloud
   ```
   *(Si no se desea subir a la nube, ejecutar sin `--cloud` y copiar el archivo resultante de `~/antigravity_backups/` a una memoria USB).*

3. **Verificar que Antigravity esté cerrado** antes de empaquetar para asegurar que las bases de datos SQLite (`conversation_summaries.db` y `<UUID>.db`) cierren sus archivos WAL y no queden transacciones en memoria.

---

## 🚨 ALERTA MANDATORIA: Después de formatear o en la nueva Surface

Cuando el usuario informe que **ya formateó** o está en una **nueva Surface / instalación limpia**:

1. **Advertir antes de abrir Antigravity:**
   > ⚠️ **IMPORTANTE:** Restaura el backup de conversaciones **antes de abrir Antigravity** por primera vez (o asegúrate de cerrarlo completamente) para evitar conflictos de sobreescritura con las bases de datos vacías iniciales.

2. **Verificar rutas absolutas del Workspace:**
   Las conversaciones guardan referencias a los proyectos con URIs absolutos (por ejemplo `file:///home/dagudelo/Code/omarchy-setup`). Asegurarse de que el usuario clone o ubique sus repositorios en la misma ruta `/home/dagudelo/Code/...`.

3. **Ejecutar la restauración:**
   - Si el archivo está local o en USB:
     ```bash
     /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh restore /ruta/al/archivo_backup.tar.gz
     ```
   - Si se guardó en Google Drive:
     ```bash
     rclone copy "gdrive:OmarchyBackups/Antigravity/" ~/antigravity_backups/ --progress
     /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh restore ~/antigravity_backups/<NOMBRE_ARCHIVO>.tar.gz
     ```

4. **Confirmar éxito:**
   Verificar con:
   ```bash
   /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh status
   ```
   Indicar al usuario que ya puede abrir Antigravity y que todo su historial, conversaciones y artefactos estarán activos.
