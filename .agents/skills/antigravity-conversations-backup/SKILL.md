---
name: antigravity-conversations-backup
description: >-
  Crea copias de seguridad y restaura conversaciones, artefactos e índices de Antigravity en la Microsoft Surface.
  Emite alertas mandatorias y guía al usuario cuando va a formatear la Surface, cambiar de máquina o después de una reinstalación limpia de Omarchy.
  Triggers: "backup conversaciones", "respaldo conversaciones", "backup antigravity", "restaurar conversaciones", "formatear surface", "cambiar de surface", "recuperar conversaciones".
---

# Antigravity Conversations Backup & Restore Skill (Surface / Omarchy)

Esta skill gestiona la preservación total del historial de conversaciones, artefactos en `brain/`, índices SQLite y estado de Google Antigravity en Omarchy.

## 🔄 Respaldo Semanal Automático (Activo)

El sistema ejecuta automáticamente un respaldo semanal a Google Drive mediante `systemd --user`:
- **Timer:** `antigravity-conversations-backup.timer` (`OnCalendar=weekly`, `Persistent=true`)
- **Destino local:** `~/antigravity_backups/` (conserva los últimos 4 backups)
- **Destino nube (Google Drive):** `gdrive:OmarchyBackups/Antigravity/` (conserva los últimos 4 backups)
- **Seguridad en caliente:** El script utiliza la API nativa de SQLite (`sqlite3 ... ".backup"`) para generar snapshots 100% consistentes sin corromper las bases de datos aunque Antigravity esté abierto.

---

## 🚨 ALERTA MANDATORIA: Antes de formatear o cambiar de Surface

Cuando el usuario mencione que va a **formatear la Surface**, **reinstalar el sistema** o **cambiar de equipo**:

1. **Emitir advertencia inmediata:**
   > ⚠️ **ALERTA CRÍTICA ANTES DE FORMATEAR / CAMBIAR DE EQUIPO:**
   > Si formateas la unidad o cambias de Surface, **las conversaciones locales posteriores al último respaldo semanal en `~/.gemini/antigravity/` se perderán** si no ejecutas un backup final ahora.

2. **Ejecutar un respaldo manual actualizado a Google Drive:**
   ```bash
   /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh backup --cloud
   ```
   *(El respaldo en caliente con SQLite `.backup` es seguro incluso con Antigravity abierto. Si prefieres USB en lugar de la nube, omite `--cloud` y copia el archivo de `~/antigravity_backups/`).*

---

## 🚨 ALERTA MANDATORIA: Después de formatear o en la nueva Surface

Cuando el usuario informe que **ya formateó** o está en una **nueva Surface / instalación limpia**:

1. **Advertir antes de abrir Antigravity:**
   > ⚠️ **IMPORTANTE:** Restaura el backup de conversaciones **antes de abrir Antigravity** por primera vez (o asegúrate de cerrarlo completamente) para evitar conflictos de sobreescritura con las bases de datos vacías iniciales.

2. **Verificar rutas absolutas del Workspace:**
   Las conversaciones guardan referencias a los proyectos con URIs absolutos (por ejemplo `file:///home/dagudelo/Code/omarchy-setup`). Asegurarse de que el usuario clone o ubique sus repositorios en la misma ruta `/home/dagudelo/Code/...`.

3. **Ejecutar la restauración:**
   - Si se guardó en Google Drive (recomendado):
     ```bash
     rclone copy "gdrive:OmarchyBackups/Antigravity/" ~/antigravity_backups/ --progress
     /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh restore ~/antigravity_backups/<NOMBRE_ARCHIVO>.tar.gz
     ```
   - Si el archivo está local o en USB:
     ```bash
     /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh restore /ruta/al/archivo_backup.tar.gz
     ```

4. **Reactivar el timer semanal en la nueva instalación:**
   ```bash
   mkdir -p ~/.config/systemd/user
   cp /home/dagudelo/Code/omarchy-setup/config/systemd/user/antigravity-conversations-backup.* ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now antigravity-conversations-backup.timer
   ```

5. **Confirmar éxito:**
   Verificar con:
   ```bash
   /home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh status
   ```
   Indicar al usuario que ya puede abrir Antigravity y que todo su historial, conversaciones y artefactos estarán activos.
