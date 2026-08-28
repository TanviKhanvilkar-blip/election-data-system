#!/bin/bash

# Election Data Management System Setup Script
# This script helps you set up the project quickly

set -e

echo "🗳️  Election Data Management System Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. You can either:"
    echo "   1. Install PostgreSQL locally"
    echo "   2. Use Docker: docker-compose up -d postgres"
    echo "   3. Use a cloud database (recommended for production)"
fi

echo "📦 Setting up virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your database credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Setup complete! Next steps:"
echo ""
echo "1. Configure your database in .env file"
echo "2. Create database: createdb election_db"
echo "3. Populate sample data: python populate_data.py"
echo "4. Run the application: python main.py"
echo "5. Open browser: http://localhost:8000"
echo ""
echo "📚 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🎉"
