#!/bin/bash

# Database Restore Script for PMCELL
# Supports both PostgreSQL and SQLite databases

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${BACKUP_DIR}/restore.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    log "${RED}ERROR: $1${NC}"
}

success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

warning() {
    log "${YELLOW}WARNING: $1${NC}"
}

# Load environment variables
load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
        log "Loaded environment variables from .env"
    elif [ -f "$PROJECT_ROOT/backend/.env" ]; then
        source "$PROJECT_ROOT/backend/.env"
        log "Loaded environment variables from backend/.env"
    else
        warning "No .env file found, using environment variables"
    fi
}

# List available backups
list_backups() {
    log "Available backups in $BACKUP_DIR:"
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "*.gz" -o -name "*.sql" -o -name "*.db" | sort -r | while read -r file; do
            local size=$(du -h "$file" | cut -f1)
            local date=$(date -r "$file" '+%Y-%m-%d %H:%M:%S')
            echo "  $(basename "$file") - $size - $date"
        done
    else
        warning "Backup directory does not exist: $BACKUP_DIR"
    fi
}

# Restore PostgreSQL database
restore_postgresql() {
    local backup_file="$1"
    local db_url="$2"
    
    log "Starting PostgreSQL restore from: $backup_file"
    
    # Extract connection parameters from DATABASE_URL
    if [[ $db_url =~ postgresql.*://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        local user="${BASH_REMATCH[1]}"
        local password="${BASH_REMATCH[2]}"
        local host="${BASH_REMATCH[3]}"
        local port="${BASH_REMATCH[4]}"
        local database="${BASH_REMATCH[5]}"
        
        export PGPASSWORD="$password"
        
        # Check if backup file is compressed
        local temp_file=""
        if [[ $backup_file == *.gz ]]; then
            temp_file="/tmp/pmcell_restore_$(date +%s).sql"
            log "Decompressing backup file..."
            if gunzip -c "$backup_file" > "$temp_file"; then
                backup_file="$temp_file"
            else
                error "Failed to decompress backup file"
                return 1
            fi
        fi
        
        # Create database if it doesn't exist
        log "Ensuring database exists..."
        createdb -h "$host" -p "$port" -U "$user" "$database" 2>/dev/null || true
        
        # Restore database
        if psql -h "$host" -p "$port" -U "$user" -d "$database" < "$backup_file"; then
            success "PostgreSQL restore completed successfully"
        else
            error "PostgreSQL restore failed"
            return 1
        fi
        
        # Cleanup temporary file
        if [ -n "$temp_file" ] && [ -f "$temp_file" ]; then
            rm "$temp_file"
        fi
        
        unset PGPASSWORD
    else
        error "Invalid PostgreSQL DATABASE_URL format"
        return 1
    fi
}

# Restore SQLite database
restore_sqlite() {
    local backup_file="$1"
    local db_path="$2"
    
    log "Starting SQLite restore from: $backup_file"
    
    # Remove sqlite+aiosqlite:/// prefix and resolve path
    db_path=$(echo "$db_path" | sed 's|sqlite+aiosqlite:///||' | sed 's|^./|'"$PROJECT_ROOT"'/backend/|')
    
    # Backup current database if it exists
    if [ -f "$db_path" ]; then
        local backup_current="${db_path}.backup.$(date +%s)"
        log "Backing up current database to: $backup_current"
        cp "$db_path" "$backup_current"
    fi
    
    # Check if backup file is compressed
    local temp_file=""
    if [[ $backup_file == *.gz ]]; then
        temp_file="/tmp/pmcell_restore_$(date +%s).db"
        log "Decompressing backup file..."
        if gunzip -c "$backup_file" > "$temp_file"; then
            backup_file="$temp_file"
        else
            error "Failed to decompress backup file"
            return 1
        fi
    fi
    
    # Restore database
    if cp "$backup_file" "$db_path"; then
        success "SQLite restore completed successfully"
    else
        error "SQLite restore failed"
        return 1
    fi
    
    # Cleanup temporary file
    if [ -n "$temp_file" ] && [ -f "$temp_file" ]; then
        rm "$temp_file"
    fi
}

# Interactive backup selection
select_backup() {
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory does not exist: $BACKUP_DIR"
        exit 1
    fi
    
    local backups=($(find "$BACKUP_DIR" -name "*.gz" -o -name "*.sql" -o -name "*.db" | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        error "No backup files found in $BACKUP_DIR"
        exit 1
    fi
    
    echo "Available backups:"
    for i in "${!backups[@]}"; do
        local file="${backups[$i]}"
        local size=$(du -h "$file" | cut -f1)
        local date=$(date -r "$file" '+%Y-%m-%d %H:%M:%S')
        echo "  $((i+1))) $(basename "$file") - $size - $date"
    done
    
    echo ""
    read -p "Select backup to restore (1-${#backups[@]}): " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le ${#backups[@]} ]; then
        echo "${backups[$((selection-1))]}"
    else
        error "Invalid selection"
        exit 1
    fi
}

# Confirmation prompt
confirm_restore() {
    local backup_file="$1"
    
    echo ""
    warning "WARNING: This will replace the current database with the backup!"
    echo "Backup file: $(basename "$backup_file")"
    echo "Database: $DATABASE_URL"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

# Main restore function
main() {
    local backup_file="$1"
    
    log "Starting PMCELL database restore..."
    
    load_env
    
    if [ -z "$DATABASE_URL" ]; then
        error "DATABASE_URL environment variable not set"
        exit 1
    fi
    
    # Select backup file if not provided
    if [ -z "$backup_file" ]; then
        backup_file=$(select_backup)
    fi
    
    # Validate backup file exists
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi
    
    # Confirm restore
    confirm_restore "$backup_file"
    
    # Perform restore based on database type
    if [[ $DATABASE_URL == postgresql* ]]; then
        restore_postgresql "$backup_file" "$DATABASE_URL"
    elif [[ $DATABASE_URL == sqlite* ]]; then
        restore_sqlite "$backup_file" "$DATABASE_URL"
    else
        error "Unsupported database type in DATABASE_URL: $DATABASE_URL"
        exit 1
    fi
    
    success "Database restore completed successfully!"
    log "Restored from: $backup_file"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "PMCELL Database Restore Script"
        echo ""
        echo "Usage: $0 [backup_file]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --list         List available backups"
        echo ""
        echo "If no backup file is specified, an interactive selection will be shown."
        echo ""
        echo "Environment Variables:"
        echo "  DATABASE_URL   Database connection string (required)"
        exit 0
        ;;
    --list)
        list_backups
        exit 0
        ;;
    "")
        main ""
        ;;
    *)
        if [ -f "$1" ]; then
            main "$1"
        else
            error "Backup file not found: $1"
            echo "Use --list to see available backups"
            exit 1
        fi
        ;;
esac