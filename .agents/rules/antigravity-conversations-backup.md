# Antigravity Conversations Backup & Migration Rule

## Purpose
Garantizar la supervivencia del historial de conversaciones, artefactos y bases de datos SQLite de Antigravity ante formateos, reinstalaciones de Omarchy o migraciones de Surface, mediante respaldo semanal automático a Google Drive y alertas preventivas.

## Automated Weekly Backup
- **Timer:** `antigravity-conversations-backup.timer` (`systemd --user`, `OnCalendar=weekly`, `Persistent=true`).
- **Cloud destination:** Google Drive vía `rclone` en `gdrive:OmarchyBackups/Antigravity/` (retención: últimos 4 backups).
- **Local destination:** `~/antigravity_backups/` (retención: últimos 4 backups).
- **Hot-backup safety:** El script usa `sqlite3 ... ".backup"` para crear snapshots consistentes sin riesgo de corrupción aunque Antigravity esté en ejecución.

## Mandatory Agent Protocol

### 1. Detección de Formateo / Migración / Cambio de Surface
Siempre que el usuario exprese la intención de formatear la Surface, reinstalar Omarchy o cambiar de máquina:
- **EMITIR ALERTA INMEDIATA**: Informar al usuario explícitamente que aunque existe un backup semanal en Google Drive (`gdrive:OmarchyBackups/Antigravity/`), cualquier conversación posterior al último respaldo se perderá si no se hace un backup final ahora.
- **Acción sugerida inmediata**: Ejecutar `/home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh backup --cloud`.

### 2. Detección de Post-Formateo / Nueva Máquina
Cuando el usuario indique que acaba de formatear o está en una nueva Surface:
- **EMITIR ALERTA DE RESTAURACIÓN**: Indicar al usuario que debe restaurar el último backup desde `gdrive:OmarchyBackups/Antigravity/` **antes de iniciar Antigravity**, o cerrar la app antes de extraer los datos.
- **Chequeo de Workspace**: Verificar que la ruta de usuario y proyectos coincida con `/home/dagudelo/Code/` para que los enlaces a proyectos no queden rotos.
- **Reactivación del timer**: Recordar habilitar nuevamente `antigravity-conversations-backup.timer` en la instalación nueva.

### 3. Componentes que deben preservarse en todo backup
Nunca respaldar únicamente un archivo individual; siempre se debe empaquetar el conjunto:
- `~/.gemini/antigravity/conversations/` (snapshots SQLite `.backup` de cada chat)
- `~/.gemini/antigravity/brain/` (artefactos y contexto persistente)
- `~/.gemini/antigravity/conversation_summaries.db` (snapshot SQLite `.backup` del índice, títulos y metadatos)
- `~/.gemini/antigravity/agyhub_summaries_proto.pb`
- `~/.gemini/antigravity/installation_id`
- `~/.gemini/antigravity/antigravity_state.pbtxt`
