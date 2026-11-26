#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Respaldo y Restauración de Conversaciones de Antigravity
# Diseñado para Omarchy Setup (Microsoft Surface y otros perfiles)
# Usa la API de backup en caliente de SQLite (.backup) para respaldos seguros
# incluso con Antigravity abierto.
# ==============================================================================

SRC_DIR="$HOME/.gemini/antigravity"
DEFAULT_DEST="$HOME/antigravity_backups"
CLOUD_REMOTE="gdrive:OmarchyBackups/Antigravity"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BACKUP_PREFIX="antigravity_conversations_backup_"
BACKUP_NAME="${BACKUP_PREFIX}${TIMESTAMP}.tar.gz"
KEEP_COUNT=4

show_help() {
    cat << EOF
Uso: $(basename "$0") [COMANDO] [OPCIONES]

Comandos:
  backup [--dest DIR] [--cloud] [--keep N]
                                  Crea un respaldo consistente (en caliente con SQLite .backup)
                                  de las conversaciones, índices y artefactos de Antigravity.
  restore <ARCHIVO.tar.gz>        Restaura conversaciones en ~/.gemini/antigravity.
  status                          Muestra el tamaño actual de las conversaciones y backups.

Opciones:
  --dest DIR    Ruta local donde guardar el backup (Por defecto: $DEFAULT_DEST)
  --cloud       Sincroniza el backup resultante a Google Drive vía rclone ($CLOUD_REMOTE)
  --keep N      Número de backups recientes a conservar (Por defecto: $KEEP_COUNT, 0 = sin límite)
  -h, --help    Muestra esta ayuda.
EOF
}

check_antigravity_running_for_restore() {
    if pgrep -f "antigravity" >/dev/null 2>&1; then
        echo "⚠️  ALERTA: Se detectó Antigravity en ejecución."
        echo "   Para restaurar sin corromper ni sobrescribir las bases de datos SQLite,"
        echo "   DEBES cerrar Antigravity primero."
        read -r -p "   ¿Deseas continuar de todas formas? (s/N): " response
        if [[ ! "$response" =~ ^([sS][iI]?|[yY][eE]?[sS]?)$ ]]; then
            echo "Operación cancelada por el usuario."
            exit 1
        fi
    fi
}

backup_sqlite_db() {
    local src_db="$1"
    local dst_db="$2"
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$src_db" ".timeout 10000" ".backup '$dst_db'"
    else
        cp -a "$src_db" "$dst_db"
    fi
}

prune_local_backups() {
    local dest_dir="$1"
    local keep="$2"
    if [ "$keep" -le 0 ] 2>/dev/null; then
        return
    fi

    mapfile -t files < <(find "$dest_dir" -maxdepth 1 -type f -name "${BACKUP_PREFIX}*.tar.gz" -printf '%T@ %p\n' | sort -rn | awk '{print $2}')
    local total="${#files[@]}"
    if [ "$total" -gt "$keep" ]; then
        echo "==> 🧹 Limpiando backups locales antiguos (conservando los últimos $keep)..."
        for ((i = keep; i < total; i++)); do
            rm -f "${files[$i]}"
            echo "   -> Eliminado local: $(basename "${files[$i]}")"
        done
    fi
}

prune_cloud_backups() {
    local keep="$1"
    if [ "$keep" -le 0 ] 2>/dev/null; then
        return
    fi

    mapfile -t remote_files < <(rclone lsf "$CLOUD_REMOTE" --files-only --include "${BACKUP_PREFIX}*.tar.gz" 2>/dev/null | sort -r)
    local total="${#remote_files[@]}"
    if [ "$total" -gt "$keep" ]; then
        echo "==> 🧹 Limpiando backups antiguos en Google Drive (conservando los últimos $keep)..."
        for ((i = keep; i < total; i++)); do
            rclone deletefile "${CLOUD_REMOTE}/${remote_files[$i]}"
            echo "   -> Eliminado en Drive: ${remote_files[$i]}"
        done
    fi
}

do_backup() {
    local dest_dir="$DEFAULT_DEST"
    local use_cloud=false
    local keep="$KEEP_COUNT"

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
            --keep)
                keep="$2"
                shift 2
                ;;
            *)
                echo "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done

    if [ ! -d "$SRC_DIR/conversations" ]; then
        echo "❌ Error: No se encontró el directorio $SRC_DIR/conversations."
        exit 1
    fi

    mkdir -p "$dest_dir"
    local target_file="$dest_dir/$BACKUP_NAME"
    STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/antigravity_backup.XXXXXX")"
    trap 'rm -rf "${STAGING_DIR:-}"' EXIT

    echo "==> 📦 Creando snapshot consistente en caliente (SQLite .backup)..."
    mkdir -p "$STAGING_DIR/conversations"

    # 1. Backup seguro de cada base de datos SQLite de conversación
    shopt -s nullglob
    local db_count=0
    for db_file in "$SRC_DIR/conversations/"*.db; do
        backup_sqlite_db "$db_file" "$STAGING_DIR/conversations/$(basename "$db_file")"
        db_count=$((db_count + 1))
    done
    shopt -u nullglob
    echo "   -> $db_count bases de datos de conversaciones respaldadas con integridad."

    # 2. Backup seguro del índice principal
    if [ -f "$SRC_DIR/conversation_summaries.db" ]; then
        backup_sqlite_db "$SRC_DIR/conversation_summaries.db" "$STAGING_DIR/conversation_summaries.db"
        echo "   -> Índice conversation_summaries.db respaldado con integridad."
    fi

    # 3. Copiar artefactos (brain) y metadatos
    if [ -d "$SRC_DIR/brain" ]; then
        cp -a "$SRC_DIR/brain" "$STAGING_DIR/brain"
        echo "   -> Carpeta brain/ (artefactos) copiada."
    fi

    for meta_file in agyhub_summaries_proto.pb installation_id antigravity_state.pbtxt; do
        if [ -f "$SRC_DIR/$meta_file" ]; then
            cp -a "$SRC_DIR/$meta_file" "$STAGING_DIR/$meta_file"
        fi
    done

    echo "==> 🗜️  Comprimiendo respaldo en $target_file..."
    tar -czf "$target_file" -C "$STAGING_DIR" .

    local size
    size="$(du -sh "$target_file" | cut -f1)"
    echo "✔ Backup local completado exitosamente: $target_file ($size)"

    prune_local_backups "$dest_dir" "$keep"

    if [ "$use_cloud" = true ]; then
        if command -v rclone >/dev/null 2>&1; then
            echo "==> ☁️  Subiendo respaldo a Google Drive ($CLOUD_REMOTE)..."
            rclone copy "$target_file" "$CLOUD_REMOTE/" --stats-one-line
            echo "✔ Sincronización a Google Drive completada."
            prune_cloud_backups "$keep"
        else
            echo "⚠️  rclone no está disponible. No se pudo sincronizar a la nube."
        fi
    fi
}

do_restore() {
    local archive="${1:-}"
    if [ -z "$archive" ] || [ ! -f "$archive" ]; then
        echo "❌ Error: Debes especificar un archivo .tar.gz válido para restaurar."
        show_help
        exit 1
    fi

    check_antigravity_running_for_restore

    echo "==> 🔄 Restaurando conversaciones en $SRC_DIR..."
    mkdir -p "$SRC_DIR"

    # Eliminar archivos WAL/SHM huérfanos para evitar conflictos con la DB restaurada
    rm -f "$SRC_DIR"/conversation_summaries.db-wal "$SRC_DIR"/conversation_summaries.db-shm
    rm -f "$SRC_DIR"/conversations/*.db-wal "$SRC_DIR"/conversations/*.db-shm

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

    if command -v rclone >/dev/null 2>&1; then
        echo ""
        echo "=== Backups en Google Drive ($CLOUD_REMOTE) ==="
        rclone lsl "$CLOUD_REMOTE" 2>/dev/null || echo "Sin backups en Google Drive todavía."
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
