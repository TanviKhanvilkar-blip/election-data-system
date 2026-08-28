-- Database initialization script for Docker PostgreSQL
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'Asia/Kolkata';

-- Create indexes for better performance (these will be created by SQLAlchemy, but keeping for reference)
-- The actual table creation will be handled by SQLAlchemy models

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE election_db TO election_user;
