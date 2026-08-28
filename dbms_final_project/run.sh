#!/bin/bash

# Election Data Management System Run Script
# This script helps you run the application easily

set -e

echo "🗳️  Starting Election Data Management System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo "🔗 Database URL: $DATABASE_URL"

# Run database migrations/setup
echo "📊 Setting up database tables..."
python -c "from app.database import create_tables; create_tables()"

# Check if we need to populate data
read -p "🌱 Do you want to populate sample data? (y/N): " populate_data
if [[ $populate_data =~ ^[Yy]$ ]]; then
    echo "📥 Populating sample data..."
    python populate_data.py
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "📱 Dashboard: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔑 Login: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python main.py
