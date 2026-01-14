# 🚀 Quick Installation & Setup Guide

## Step-by-Step Installation

### 1. Prerequisites

**Required Software:**
- Python 3.8 or higher
- MetaTrader 5 terminal (with active account)
- 4GB+ RAM recommended

**Check Python Version:**
```bash
python --version
# Should show Python 3.8.x or higher
```

---

### 2. Install Dependencies

```bash
# Navigate to project directory
cd GOLD-MODEL

# Install all required packages
pip install -r requirements.txt
```

**Package Installation Time:** ~2-3 minutes

**If you encounter errors:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages one by one
pip install MetaTrader5
pip install pandas numpy
pip install xgboost scikit-learn optuna
pip install ta yfinance
```

---

### 3. MetaTrader 5 Setup

#### Windows:
1. Download MT5 from your broker's website
2. Install and login with your account credentials
3. Ensure **"Allow algorithmic trading"** is enabled:
   - Tools → Options → Expert Advisors → ✅ Allow algorithmic trading

#### Linux/Mac:
```bash
# Install Wine (for running Windows applications)
# Ubuntu/Debian:
sudo apt-get install wine64

# Mac:
brew install --cask wine-stable

# Then install MT5 using Wine
wine MT5Setup.exe
```

#### Verify MT5 Connection:
```python
import MetaTrader5 as mt5

if mt5.initialize():
    print("✅ MT5 connected successfully!")
    print(f"MT5 Version: {mt5.version()}")
    mt5.shutdown()
else:
    print("❌ MT5 connection failed")
```

---

### 4. Configure XAUUSD Symbol

In MetaTrader 5:
1. Right-click on **Market Watch**
2. Select **Symbols**
3. Search for **XAUUSD** (or XAU/USD)
4. Click **Show** to enable the symbol
5. Verify you can see the price chart

---

### 5. Quick Test Run

```bash
# Run the quick start script
python quick_start.py
```

**Select Option 1** (Quick Test) for a 5-minute test run.

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║   🏆 GOLD TRADING ML SYSTEM - QUICK START 🏆                 ║
╚═══════════════════════════════════════════════════════════════╝

Select option (1-4): 1

✅ MT5 initialized successfully
📥 Fetching 10000 candles for XAUUSD...
✅ Fetched 10000 candles for XAUUSD
🧠 Engineering Advanced Features...
...
✅ Optimization complete!
🏆 Best F1-Score: 0.6234
```

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: MT5 initialization failed
**Error:** `MT5 initialization failed, error code: ...`

**Solution:**
```bash
# Make sure MT5 is running in the background
# Restart MT5 terminal
# Check if you're logged into your account
```

### Issue 2: Symbol not found
**Error:** `Failed to fetch data for XAUUSD`

**Solution:**
- Enable XAUUSD in Market Watch (see Step 4)
- Try alternative symbols: `GOLD`, `XAUUSD.m`, `XAUUSD.raw`
- Check with your broker if Gold trading is available

### Issue 3: Python package conflicts
**Error:** `ImportError: cannot import name ...`

**Solution:**
```bash
# Create a fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 4: Insufficient historical data
**Error:** `Fetched 0 candles` or too few candles

**Solution:**
```python
# In config.py, reduce n_candles
MT5_CONFIG = {
    'n_candles': 10000,  # Start with smaller dataset
}
```

### Issue 5: USD Index not found
**Warning:** `Could not fetch USD Index data`

**This is OK!** The pipeline will continue without USD Index data. The model will work, but with slightly reduced accuracy.

---

## ⚡ Quick Performance Tips

### Speed Up Training:
```python
# In config.py
OPTUNA_CONFIG = {
    'n_trials': 20,  # Reduce from 50
}

VALIDATION_CONFIG = {
    'cv_splits': 3,  # Reduce from 5
}
```

### Use GPU (if available):
```python
# In config.py
ADVANCED_CONFIG = {
    'use_gpu': True,
}

MODEL_CONFIG = {
    'tree_method': 'gpu_hist',  # Change from 'hist'
}
```

---

## 📂 Project Structure

```
GOLD-MODEL/
├── gold_trading_ml_pipeline.py  # Main pipeline (CORE)
├── config.py                    # Configuration settings
├── quick_start.py               # Easy start script
├── examples.py                  # Usage examples
├── evaluation_utils.py          # Backtesting tools
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
└── .gitignore                   # Git ignore rules
```

---

## 🎯 Next Steps After Installation

### 1. Run Quick Test (5 minutes)
```bash
python quick_start.py
# Select option 1
```

### 2. Run Balanced Mode (25 minutes)
```bash
python quick_start.py
# Select option 2
```

### 3. Explore Examples
```bash
python examples.py
```

### 4. Customize Configuration
Edit `config.py` to adjust:
- Confidence threshold
- Risk per trade
- Optuna trials
- Feature engineering parameters

### 5. Live Trading (Paper Trading First!)
```python
# See examples.py - Example 3
# Generate live signals and test manually
# DO NOT use real money until fully tested!
```

---

## 📞 Support

**Common Questions:**

**Q: How long does training take?**
A: Quick test: 5 min, Balanced: 25 min, Production: 45-60 min

**Q: Can I use other symbols?**
A: Yes! Change `symbol` in config.py to any MT5 symbol (EURUSD, BTCUSD, etc.)

**Q: Do I need a VPS?**
A: Not required, but recommended for 24/7 automated trading

**Q: Is this profitable?**
A: Past performance ≠ future results. Always test thoroughly!

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] MetaTrader 5 installed and running
- [ ] MT5 account logged in
- [ ] `pip install -r requirements.txt` completed
- [ ] XAUUSD symbol enabled in Market Watch
- [ ] `python quick_start.py` runs successfully
- [ ] First model trained with >60% precision

---

## 🎉 You're Ready!

If all checks pass, you're ready to start building ML trading models!

**Recommended Learning Path:**
1. Run quick test to familiarize yourself
2. Study the feature engineering in the code
3. Experiment with different thresholds
4. Backtest thoroughly before live trading
5. Start with paper trading (demo account)

**Happy Trading! 📈**
