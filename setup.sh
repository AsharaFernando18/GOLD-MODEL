#!/bin/bash

# Quick setup script for Gold Trading ML System

echo "=================================="
echo " Gold Trading ML System - Setup"
echo "=================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Install requirements
echo ""
echo "📦 Installing Python packages..."
pip install pandas numpy yfinance xgboost scikit-learn optuna ta matplotlib seaborn python-dateutil

# Note about MT5
echo ""
echo "⚠️  NOTE: MetaTrader5 library is Windows-only."
echo "   On Windows, install with: pip install MetaTrader5"
echo "   On Linux/Mac, the system will use mock mode for testing."

# Run test
echo ""
echo "🧪 Running comprehensive test..."
python test_pipeline.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review config.py to adjust parameters"
echo "2. Run: python quick_start.py"
echo "3. Or: python gold_trading_ml_pipeline.py"
echo ""
