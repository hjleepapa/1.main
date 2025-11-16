#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Skipping FrontMCP build (Frontegg disabled)."

echo "Build complete!"

