#!/bin/bash

# Quick memory fix for Render deployment

echo "🚀 Applying quick memory fix..."

# 1. Backup original files
echo "📦 Backing up original files..."
cp requirements.txt requirements_backup.txt
cp app.py app_backup.py
cp passenger_wsgi.py passenger_wsgi_backup.py
cp render.yaml render_backup.yaml

# 2. Apply memory optimizations
echo "🔄 Applying memory optimizations..."

# Replace requirements with lightweight version
cp requirements_memory_optimized.txt requirements.txt

# Replace app with memory-optimized version
cp app_memory_optimized.py app.py

# Replace WSGI with memory-optimized version
cp passenger_wsgi_memory_optimized.py passenger_wsgi.py

# Replace render config with memory-optimized version
cp render_memory_optimized.yaml render.yaml

echo "✅ Memory optimizations applied!"
echo "📊 Expected memory reduction: ~600MB → ~400MB"
echo "🔧 Ready for deployment with Render free tier"
