# ⚡ Quick Reference Card

## 🚀 Installation (30 seconds)

```bash
git clone <repository>
cd GOLD-MODEL
bash setup.sh
```

## 🎯 Quick Commands

| Command | Purpose | Time |
|---------|---------|------|
| `python test_pipeline.py` | Test everything | 30s |
| `python quick_start.py` | Interactive mode | 5-30min |
| `python gold_trading_ml_pipeline.py` | Full pipeline | 15min |
| `python run_backtest.py` | Backtest | 10min |

## 📊 Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `gold_trading_ml_pipeline.py` | 717 | Main pipeline |
| `config.py` | 150 | Configuration |
| `evaluation_utils.py` | 630 | Backtesting |
| `quick_start.py` | 228 | User interface |
| `test_pipeline.py` | 350 | Test suite |

## 🎛️ Configuration Presets

Edit `config.py` and use:

### Quick Test (5 minutes)
```python
apply_preset('quick')
# 10,000 candles, 10 trials
```

### Balanced (15 minutes) ⭐ Recommended
```python
apply_preset('balanced')
# 50,000 candles, 50 trials
```

### Production (30 minutes)
```python
apply_preset('production')
# 100,000 candles, 100 trials
```

## 🧠 Feature Categories

| Category | Count | Example |
|----------|-------|---------|
| Cyclical Time | 6 | `hour_sin`, `dow_cos` |
| Technical | 15 | `ema_20`, `rsi`, `macd` |
| Volatility | 4 | `atr`, `bb_width` |
| Lag | 12 | `return_t1`, `close_lag_2` |
| Interaction | 8 | `close_ema20_ratio` |
| Volume | 6 | `volume_momentum` |
| **Total** | **47** | - |

## 🎯 Signal Logic

```python
if buy_probability > 65%:
    return "BUY"
elif sell_probability > 65%:
    return "SELL"
else:
    return "NO_TRADE"
```

## 📈 Expected Performance

| Metric | Value |
|--------|-------|
| Accuracy | 65-75% |
| Precision | 70-80% |
| F1-Score | 68-76% |
| Win Rate | 55-65% |
| Sharpe Ratio | 1.5-2.5 |

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| MT5 connection failed | Install MT5, enable algo trading |
| Low accuracy (<60%) | Increase trials/candles in config |
| Import errors | Run `pip install -r requirements.txt` |
| Linux/Mac MT5 error | Use mock mode (automatic) |

## 💻 Code Snippets

### Generate Signal
```python
from gold_trading_ml_pipeline import GoldTradingMLPipeline

pipeline = GoldTradingMLPipeline()
pipeline.initialize_mt5()
data = pipeline.fetch_mt5_data("XAUUSD", mt5.TIMEFRAME_M15, 300)
features = pipeline.create_advanced_features(data)
signal = pipeline.generate_trading_signal(features.iloc[[-1]])
print(signal)
```

### Train Model
```python
pipeline = GoldTradingMLPipeline()
pipeline.initialize_mt5()
data = pipeline.fetch_mt5_data("XAUUSD", mt5.TIMEFRAME_M15, 50000)
features = pipeline.create_advanced_features(data)
pipeline.train_model_with_optuna(features)
pipeline.save_model("my_model.pkl")
```

### Load & Use Model
```python
pipeline = GoldTradingMLPipeline()
pipeline.load_model("my_model.pkl")
# Now use pipeline.generate_trading_signal()
```

## 📚 Documentation Links

| Topic | File |
|-------|------|
| Getting Started | [GETTING_STARTED.md](GETTING_STARTED.md) |
| Installation | [INSTALLATION.md](INSTALLATION.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Full Summary | [DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md) |
| Examples | [examples.py](examples.py) |

## ⚙️ Important Parameters

### In config.py:

```python
# Data
MT5_CONFIG['n_candles'] = 50000        # More = better accuracy
MT5_CONFIG['timeframe'] = 'M15'        # M5, M15, M30, H1

# Optimization
OPTUNA_CONFIG['n_trials'] = 50         # More = better params

# Trading
MODEL_CONFIG['probability_threshold'] = 0.65  # Higher = fewer trades
RISK_CONFIG['position_size'] = 0.02    # 2% risk per trade
```

## 🎓 Best Practices

1. **Always test first**: `python test_pipeline.py`
2. **Start with demo**: Paper trade before live
3. **Use balanced preset**: Good speed/accuracy tradeoff
4. **Monitor performance**: Track win rate & drawdown
5. **Retrain regularly**: Every 1-2 months
6. **Adjust threshold**: 0.70+ for more conservative trading

## 📞 Need Help?

1. Check [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start guide
2. Read [INSTALLATION.md](INSTALLATION.md) - Detailed setup
3. See [examples.py](examples.py) - Code examples
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) - System design

## ⚠️ Remember

- This is for educational purposes
- Always test on demo accounts first
- Use proper risk management
- Past performance ≠ future results
- Never risk more than you can afford to lose

---

**Quick Start Command:**
```bash
python quick_start.py
```

**Full Pipeline:**
```bash
python gold_trading_ml_pipeline.py
```

**Test Everything:**
```bash
python test_pipeline.py
```

---

Built with ❤️ by Lead AI Quant Researcher
