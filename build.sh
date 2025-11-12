#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting Convonet build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install additional team collaboration dependencies
if [ -f "requirements_team_collaboration.txt" ]; then
    echo "📦 Installing team collaboration dependencies..."
    pip install -r requirements_team_collaboration.txt
fi

# Run database migration
echo "🔄 Running database migration..."
python run_migration.py

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi
