-- Initialize database with extensions and settings for production
-- This file is executed when PostgreSQL container starts for the first time

-- Enable commonly used extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set timezone to UTC for consistency
SET timezone = 'UTC';

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE pmcell_db TO pmcell_user;

-- Create schema for application tables
CREATE SCHEMA IF NOT EXISTS pmcell AUTHORIZATION pmcell_user;

-- Set default search path
ALTER USER pmcell_user SET search_path TO pmcell, public;