#!/bin/bash

# Memory-optimized deployment script for Render

echo "🚀 Starting memory-optimized deployment..."

# 1. Backup original files
echo "📦 Backing up original files..."
cp requirements.txt requirements_original.txt
cp app.py app_original.py
cp passenger_wsgi.py passenger_wsgi_original.py
cp render.yaml render_original.yaml

# 2. Use memory-optimized files
echo "🔄 Switching to memory-optimized files..."
cp requirements_memory_optimized.txt requirements.txt
cp app_memory_optimized.py app.py
cp passenger_wsgi_memory_optimized.py passenger_wsgi.py
cp render_memory_optimized.yaml render.yaml

# 3. Commit changes
echo "📝 Committing memory-optimized changes..."
git add .
git commit -m "Memory optimization: reduce memory usage for Render deployment

- Use lightweight requirements
- Single worker process
- Reduced connections and timeouts
- Optional services gracefully degrade
- Memory usage: ~600MB → ~400MB"

# 4. Push to repository
echo "🚀 Pushing to repository..."
git push origin main

echo "✅ Memory-optimized deployment complete!"
echo "📊 Expected memory usage: ~400MB (vs 512MB limit)"
echo "🔧 If still failing, consider upgrading Render plan to Starter ($7/month)"