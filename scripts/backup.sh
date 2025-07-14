#!/bin/bash

# Database Backup Script for PMCELL
# Supports both PostgreSQL and SQLite databases

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${BACKUP_DIR}/backup.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

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

# Create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log "Created backup directory: $BACKUP_DIR"
    fi
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

# Backup PostgreSQL database
backup_postgresql() {
    local db_url="$1"
    local backup_file="${BACKUP_DIR}/postgresql_backup_${TIMESTAMP}.sql"
    
    log "Starting PostgreSQL backup..."
    
    # Extract connection parameters from DATABASE_URL
    # Format: postgresql+asyncpg://user:password@host:port/database
    if [[ $db_url =~ postgresql.*://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        local user="${BASH_REMATCH[1]}"
        local password="${BASH_REMATCH[2]}"
        local host="${BASH_REMATCH[3]}"
        local port="${BASH_REMATCH[4]}"
        local database="${BASH_REMATCH[5]}"
        
        export PGPASSWORD="$password"
        
        if pg_dump -h "$host" -p "$port" -U "$user" -d "$database" > "$backup_file"; then
            success "PostgreSQL backup completed: $backup_file"
            
            # Compress backup
            if gzip "$backup_file"; then
                success "Backup compressed: ${backup_file}.gz"
                echo "${backup_file}.gz"
            else
                warning "Failed to compress backup"
                echo "$backup_file"
            fi
        else
            error "PostgreSQL backup failed"
            return 1
        fi
        
        unset PGPASSWORD
    else
        error "Invalid PostgreSQL DATABASE_URL format"
        return 1
    fi
}

# Backup SQLite database
backup_sqlite() {
    local db_path="$1"
    local backup_file="${BACKUP_DIR}/sqlite_backup_${TIMESTAMP}.db"
    
    log "Starting SQLite backup..."
    
    # Remove sqlite+aiosqlite:/// prefix and resolve path
    db_path=$(echo "$db_path" | sed 's|sqlite+aiosqlite:///||' | sed 's|^./|'"$PROJECT_ROOT"'/backend/|')
    
    if [ -f "$db_path" ]; then
        if cp "$db_path" "$backup_file"; then
            success "SQLite backup completed: $backup_file"
            
            # Compress backup
            if gzip "$backup_file"; then
                success "Backup compressed: ${backup_file}.gz"
                echo "${backup_file}.gz"
            else
                warning "Failed to compress backup"
                echo "$backup_file"
            fi
        else
            error "SQLite backup failed"
            return 1
        fi
    else
        error "SQLite database file not found: $db_path"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    local deleted_count=0
    while IFS= read -r -d '' file; do
        rm "$file"
        deleted_count=$((deleted_count + 1))
        log "Deleted old backup: $(basename "$file")"
    done < <(find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS -print0)
    
    if [ $deleted_count -eq 0 ]; then
        log "No old backups to clean up"
    else
        success "Cleaned up $deleted_count old backup(s)"
    fi
}

# Upload backup to cloud storage (optional)
upload_to_cloud() {
    local backup_file="$1"
    
    if [ -n "$AWS_S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then
        log "Uploading backup to S3..."
        if aws s3 cp "$backup_file" "s3://$AWS_S3_BUCKET/pmcell-backups/$(basename "$backup_file")"; then
            success "Backup uploaded to S3"
        else
            warning "Failed to upload backup to S3"
        fi
    elif [ -n "$BACKUP_WEBHOOK_URL" ]; then
        log "Sending backup notification..."
        curl -X POST "$BACKUP_WEBHOOK_URL" \
             -H "Content-Type: application/json" \
             -d "{\"text\":\"PMCELL backup completed: $(basename "$backup_file")\"}" \
             >/dev/null 2>&1 || warning "Failed to send backup notification"
    fi
}

# Main backup function
main() {
    log "Starting PMCELL database backup..."
    
    create_backup_dir
    load_env
    
    if [ -z "$DATABASE_URL" ]; then
        error "DATABASE_URL environment variable not set"
        exit 1
    fi
    
    local backup_file=""
    
    if [[ $DATABASE_URL == postgresql* ]]; then
        backup_file=$(backup_postgresql "$DATABASE_URL")
    elif [[ $DATABASE_URL == sqlite* ]]; then
        backup_file=$(backup_sqlite "$DATABASE_URL")
    else
        error "Unsupported database type in DATABASE_URL: $DATABASE_URL"
        exit 1
    fi
    
    if [ -n "$backup_file" ]; then
        upload_to_cloud "$backup_file"
        cleanup_old_backups
        success "Backup process completed successfully"
        
        # Print backup info
        log "Backup file: $backup_file"
        log "Backup size: $(du -h "$backup_file" | cut -f1)"
    else
        error "Backup process failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "PMCELL Database Backup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --cleanup      Only run cleanup of old backups"
        echo "  --test         Test backup configuration"
        echo ""
        echo "Environment Variables:"
        echo "  DATABASE_URL        Database connection string (required)"
        echo "  AWS_S3_BUCKET      S3 bucket for backup storage (optional)"
        echo "  BACKUP_WEBHOOK_URL Webhook URL for notifications (optional)"
        exit 0
        ;;
    --cleanup)
        create_backup_dir
        cleanup_old_backups
        exit 0
        ;;
    --test)
        create_backup_dir
        load_env
        log "Testing backup configuration..."
        log "DATABASE_URL: ${DATABASE_URL:-'not set'}"
        log "Backup directory: $BACKUP_DIR"
        log "AWS S3 Bucket: ${AWS_S3_BUCKET:-'not configured'}"
        log "Webhook URL: ${BACKUP_WEBHOOK_URL:-'not configured'}"
        success "Configuration test completed"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac