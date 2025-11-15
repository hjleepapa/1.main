#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building FrontMCP server..."
cd frontmcp
npm install
npm run build
cd ..

echo "Build complete!"

