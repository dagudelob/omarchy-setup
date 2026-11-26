#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Respaldo y Restauración de Conversaciones de Antigravity
# Diseñado para Omarchy Setup (Microsoft Surface y otros perfiles)
# ==============================================================================

SRC_DIR="$HOME/.gemini/antigravity"
DEFAULT_DEST="$HOME/antigravity_backups"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BACKUP_NAME="antigravity_conversations_backup_${TIMESTAMP}.tar.gz"

show_help() {
    cat << EOF
Uso: $(basename "$0") [COMANDO] [OPCIONES]

Comandos:
  backup [--dest DIR] [--cloud]   Crea un archivo comprimido con las conversaciones,
                                  índices y artefactos de Antigravity.
  restore <ARCHIVO.tar.gz>        Restaura conversaciones en ~/.gemini/antigravity.
  status                          Muestra el tamaño actual de las conversaciones y backups locales.

Opciones:
  --dest DIR    Ruta donde guardar el backup (Por defecto: $DEFAULT_DEST)
  --cloud       Sincroniza el backup resultante a Google Drive vía rclone (gdrive:OmarchyBackups)
  -h, --help    Muestra esta ayuda.
EOF
}

check_antigravity_running() {
    if pgrep -f "antigravity" >/dev/null 2>&1; then
        echo "⚠️  ALERTA: Se detectó Antigravity en ejecución."
        echo "   Para evitar inconsistencias en las bases de datos SQLite (WAL/SHM),"
        echo "   se recomienda cerrar Antigravity antes de respaldar o restaurar."
        read -r -p "   ¿Deseas continuar de todas formas? (s/N): " response
        if [[ ! "$response" =~ ^([sS][iI]?|[yY][eE]?[sS]?)$ ]]; then
            echo "Operación cancelada por el usuario."
            exit 1
        fi
    fi
}

do_backup() {
    local dest_dir="$DEFAULT_DEST"
    local use_cloud=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dest)
                dest_dir="$2"
                shift 2
                ;;
            --cloud)
                use_cloud=true
                shift
                ;;
            *)
                echo "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done

    check_antigravity_running

    if [ ! -d "$SRC_DIR/conversations" ]; then
        echo "❌ Error: No se encontró el directorio $SRC_DIR/conversations."
        exit 1
    fi

    mkdir -p "$dest_dir"
    local target_file="$dest_dir/$BACKUP_NAME"

    echo "==> 📦 Creando copia de seguridad de conversaciones de Antigravity..."
    echo "    Origen: $SRC_DIR"
    echo "    Destino: $target_file"

    tar -czf "$target_file" \
        -C "$SRC_DIR" \
        conversations \
        brain \
        conversation_summaries.db \
        conversation_summaries.db-shm 2>/dev/null || true \
        conversation_summaries.db-wal 2>/dev/null || true \
        agyhub_summaries_proto.pb 2>/dev/null || true \
        installation_id 2>/dev/null || true \
        antigravity_state.pbtxt 2>/dev/null || true

    local size
    size="$(du -sh "$target_file" | cut -f1)"
    echo "✔ Backup local completado exitosamente: $target_file ($size)"

    if [ "$use_cloud" = true ]; then
        if command -v rclone >/dev/null 2>&1; then
            echo "==> ☁️  Sincronizando con Google Drive (rclone)..."
            rclone copy "$target_file" "gdrive:OmarchyBackups/Antigravity/" --progress
            echo "✔ Sincronización a la nube completada."
        else
            echo "⚠️  rclone no está disponible. No se pudo sincronizar a la nube."
        fi
    fi

    echo ""
    echo "📢 IMPORTANTE: Guarda este archivo ($target_file) en una memoria USB o nube antes de formatear."
}

do_restore() {
    local archive="${1:-}"
    if [ -z "$archive" ] || [ ! -f "$archive" ]; then
        echo "❌ Error: Debes especificar un archivo .tar.gz válido para restaurar."
        show_help
        exit 1
    fi

    check_antigravity_running

    echo "==> 🔄 Restaurando conversaciones en $SRC_DIR..."
    mkdir -p "$SRC_DIR"

    tar -xzf "$archive" -C "$SRC_DIR"

    echo "✔ Conversaciones restauradas correctamente."
    echo "   Al abrir Antigravity, tu historial y artefactos estarán disponibles."
}

do_status() {
    echo "=== Estado de Datos de Antigravity ==="
    if [ -d "$SRC_DIR" ]; then
        du -sh "$SRC_DIR/conversations" 2>/dev/null || echo "Sin conversaciones."
        du -sh "$SRC_DIR/brain" 2>/dev/null || echo "Sin artefactos en brain."
        du -sh "$SRC_DIR"/conversation_summaries.db* 2>/dev/null || true
    else
        echo "No se encontró instalación de Antigravity en $SRC_DIR."
    fi

    echo ""
    echo "=== Backups Locales ($DEFAULT_DEST) ==="
    if [ -d "$DEFAULT_DEST" ]; then
        ls -lh "$DEFAULT_DEST"
    else
        echo "No existen backups locales aún en $DEFAULT_DEST."
    fi
}

# --- Entrada principal ---
CMD="${1:-}"
shift || true

case "$CMD" in
    backup)
        do_backup "$@"
        ;;
    restore)
        do_restore "$@"
        ;;
    status)
        do_status
        ;;
    -h|--help|"")
        show_help
        ;;
    *)
        echo "Comando no reconocido: $CMD"
        show_help
        exit 1
        ;;
esac
