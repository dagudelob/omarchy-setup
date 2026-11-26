# Antigravity Conversations Backup & Migration Rule

## Purpose
Garantizar la supervivencia del historial de conversaciones, artefactos y bases de datos SQLite de Antigravity ante formateos, reinstalaciones de Omarchy o migraciones de Surface.

## Mandatory Agent Protocol

### 1. Detección de Formateo / Migración / Cambio de Surface
Siempre que el usuario exprese la intención de formatear la Surface, reinstalar Omarchy o cambiar de máquina:
- **EMITIR ALERTA INMEDIATA**: Informar al usuario explícitamente que las conversaciones de Antigravity **NO** se sincronizan solas en Git ni en la nube por defecto y se borrarán por completo si no se respaldan.
- **Acción sugerida inmediata**: Ejecutar `/home/dagudelo/Code/omarchy-setup/scripts/backup-antigravity-conversations.sh backup --cloud` o exportar a USB.

### 2. Detección de Post-Formateo / Nueva Máquina
Cuando el usuario indique que acaba de formatear o está en una nueva Surface:
- **EMITIR ALERTA DE RESTAURACIÓN**: Indicar al usuario que debe restaurar el backup con el script antes de iniciar Antigravity, o cerrar la app antes de extraer los datos.
- **Chequeo de Workspace**: Verificar que la ruta de usuario y proyectos coincida con `/home/dagudelo/Code/` para que los enlaces a proyectos no queden rotos.

### 3. Componentes que deben preservarse en todo backup
Nunca respaldar únicamente un archivo individual; siempre se debe empaquetar el conjunto:
- `~/.gemini/antigravity/conversations/` (bases de datos SQLite de cada chat)
- `~/.gemini/antigravity/brain/` (artefactos y contexto persistente)
- `~/.gemini/antigravity/conversation_summaries.db*` (índice, títulos y metadatos)
- `~/.gemini/antigravity/agyhub_summaries_proto.pb`
- `~/.gemini/antigravity/installation_id`
- `~/.gemini/antigravity/antigravity_state.pbtxt`
