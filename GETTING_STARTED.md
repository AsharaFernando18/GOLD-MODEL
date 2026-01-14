# 🚀 GETTING STARTED GUIDE

## Quick Start (5 Minutes)

### 1. **Installation**

```bash
# Clone or download the repository
cd GOLD-MODEL

# Run automated setup
bash setup.sh
```

Or manual installation:
```bash
# Install dependencies
pip install pandas numpy yfinance xgboost scikit-learn optuna ta matplotlib seaborn

# On Windows only: Install MetaTrader5
pip install MetaTrader5
```

### 2. **Test the System**

```bash
# Run comprehensive test (no MT5 required)
python test_pipeline.py
```

Expected output:
```
✅ All tests passed successfully!
   Average Accuracy: 71.03%
   Average F1-Score: 68.74%
```

### 3. **Configure (Optional)**

Edit [config.py](config.py) to adjust:
- Number of candles (default: 50,000)
- Optuna trials (default: 50)
- Probability threshold (default: 0.65)
- Risk management parameters

### 4. **Run the Pipeline**

#### Option A: Interactive Quick Start
```bash
python quick_start.py
```

Choose from presets:
- **Quick Test**: 10k candles, 10 trials (~5 min)
- **Balanced**: 50k candles, 50 trials (~15 min)  ⭐ Recommended
- **Production**: 100k candles, 100 trials (~30 min)

#### Option B: Full Pipeline
```bash
python gold_trading_ml_pipeline.py
```

#### Option C: Backtest Mode
```bash
python run_backtest.py
```

---

## 📊 What to Expect

### First Run Output:
```
🔌 Initializing MetaTrader 5...
   ✅ Connected to MT5 Terminal

📥 Fetching XAUUSD M15 Data...
   ✅ Fetched 50,000 candles

💱 Fetching USD Index for correlation...
   ✅ Merged USD correlation data

🧠 Engineering 47 Advanced Features...
   ✅ Features created

🔬 Optuna Hyperparameter Optimization...
   Trial 10/50: F1=0.723
   Trial 20/50: F1=0.735
   ...
   ✅ Best parameters found!

🎯 Training Final Model...
   ✅ Model trained successfully

📊 Model Performance:
   Accuracy:  72.45%
   Precision: 78.32%
   F1-Score:  75.21%

💾 Saving model to: models/gold_xgboost_20260114.pkl
   ✅ Model saved!
```

---

## 🎯 Using the Model

### Generate Live Signals

```python
from gold_trading_ml_pipeline import GoldTradingMLPipeline
import MetaTrader5 as mt5

# Initialize pipeline
pipeline = GoldTradingMLPipeline()
pipeline.initialize_mt5()

# Fetch latest data
data = pipeline.fetch_mt5_data("XAUUSD", mt5.TIMEFRAME_M15, 300)

# Create features
features = pipeline.create_advanced_features(data)

# Generate signal
signal = pipeline.generate_trading_signal(features.iloc[[-1]], threshold=0.65)

print(f"Signal: {signal['signal']}")
print(f"Confidence: {signal['confidence']*100:.2f}%")
```

Output:
```
Signal: BUY
Confidence: 72.45%
```

### Understanding Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| **BUY** | Model is >65% confident price will rise | Open long position |
| **SELL** | Model is >65% confident price will fall | Open short position |
| **NO_TRADE** | Confidence is 40-65% (uncertain) | Stay out of market |

---

## 🔧 Troubleshooting

### ❌ "MT5 initialization failed"

**On Windows:**
1. Install MetaTrader 5 terminal
2. Open MT5 and login
3. Enable "Algorithmic Trading" button
4. Run script again

**On Linux/Mac:**
- MT5 is Windows-only
- System will use mock mode for testing
- For production, deploy on Windows VPS

### ❌ "No data fetched"

Check:
1. MT5 terminal is open and connected
2. Symbol "XAUUSD" is in Market Watch
3. Sufficient historical data is available

### ❌ Low accuracy (<60%)

Try:
1. Increase Optuna trials: `OPTUNA_CONFIG['n_trials'] = 100`
2. Increase candle count: `MT5_CONFIG['n_candles'] = 100000`
3. Change timeframe: `MT5_CONFIG['timeframe'] = 'M5'`
4. Adjust threshold: `MODEL_CONFIG['probability_threshold'] = 0.70`

---

## 📈 Performance Optimization

### For Speed:
```python
# In config.py
OPTUNA_CONFIG['n_trials'] = 20  # Reduce trials
MT5_CONFIG['n_candles'] = 20000  # Fewer candles
```

### For Accuracy:
```python
# In config.py
OPTUNA_CONFIG['n_trials'] = 100  # More trials
MT5_CONFIG['n_candles'] = 100000  # More data
MODEL_CONFIG['probability_threshold'] = 0.70  # Higher threshold
```

### For Live Trading:
```python
# In config.py
MODEL_CONFIG['probability_threshold'] = 0.75  # Be conservative
RISK_CONFIG['position_size'] = 0.02  # Risk 2% per trade
```

---

## 🎓 Understanding the Code

### Key Files:

| File | Purpose |
|------|---------|
| `gold_trading_ml_pipeline.py` | Main pipeline class (700+ lines) |
| `config.py` | All configurable parameters |
| `evaluation_utils.py` | Backtesting & evaluation tools |
| `quick_start.py` | Interactive launcher with presets |
| `run_backtest.py` | Full backtesting simulation |
| `test_pipeline.py` | Comprehensive test suite |

### Feature Engineering Highlights:

The "brain" of the system creates **47 features**:

1. **Cyclical Time** (6 features)
   - Hour/Day encoded as sine/cosine
   - Captures market session patterns

2. **Technical Indicators** (15 features)
   - EMAs, RSI, Stochastic, ADX, MACD
   - Bollinger Bands, ATR

3. **Lag Features** (12 features)
   - Returns at t-1, t-2, t-3, t-5
   - Price momentum patterns

4. **Interaction Features** (8 features)
   - Price/EMA ratios
   - Gold/USD correlation
   - Volatility regimes

5. **Volume Features** (6 features)
   - Volume momentum
   - Volume ratios

---

## 📚 Next Steps

1. **Paper Trade**: Test signals with demo account first
2. **Optimize**: Run backtests to find best parameters for your broker
3. **Deploy**: Move to VPS for 24/7 operation
4. **Monitor**: Track performance and retrain monthly

---

## 🆘 Support

Found a bug? Have questions?

1. Check [INSTALLATION.md](INSTALLATION.md) for detailed setup
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture
3. See [examples.py](examples.py) for more code examples

---

**⚠️ IMPORTANT DISCLAIMER**

This is an educational/research tool. Trading involves substantial risk of loss. Always:
- Test thoroughly on demo accounts
- Start with small position sizes
- Use proper risk management
- Never risk more than you can afford to lose

Past performance does not guarantee future results.

---

**Built with ❤️ by Lead AI Quant Researcher**

*Precision over frequency. Intelligence over emotion.*
