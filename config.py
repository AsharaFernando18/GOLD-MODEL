"""
Configuration file for Gold Trading ML Pipeline
Modify these parameters to customize the system
"""

# ==================== MT5 CONNECTION ====================
MT5_CONFIG = {
    'symbol': 'XAUUSD',              # Trading symbol
    'timeframe': 'M15',              # Options: M1, M5, M15, M30, H1, H4, D1
    'n_candles': 50000,              # Number of historical candles to fetch
    'usd_symbols': ['USDX', 'DXY', 'USDDX'],  # USD Index symbols to try in MT5
}

# ==================== FEATURE ENGINEERING ====================
FEATURE_CONFIG = {
    'ema_periods': [20, 50, 200],    # EMA periods
    'rsi_period': 14,                # RSI period
    'atr_period': 14,                # ATR period
    'bb_period': 20,                 # Bollinger Bands period
    'bb_std': 2,                     # Bollinger Bands standard deviation
    'stoch_period': 14,              # Stochastic Oscillator period
    'stoch_smooth': 3,               # Stochastic smoothing
    'adx_period': 14,                # ADX period
    'macd_fast': 12,                 # MACD fast EMA
    'macd_slow': 26,                 # MACD slow EMA
    'macd_signal': 9,                # MACD signal line
    'lag_periods': [1, 2, 3],        # Lag periods for returns
    'volume_ma_period': 20,          # Volume moving average period
    'correlation_period': 50,        # Gold-USD correlation period
}

# ==================== MODEL TRAINING ====================
MODEL_CONFIG = {
    # XGBoost fixed parameters
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'random_state': 42,
    'tree_method': 'hist',           # Options: 'hist', 'gpu_hist', 'exact'
    'n_jobs': -1,                    # Use all CPU cores
    
    # Optuna hyperparameter search space
    'learning_rate_range': (0.01, 0.3),
    'max_depth_range': (3, 10),
    'n_estimators_range': (100, 1000),
    'min_child_weight_range': (1, 7),
    'subsample_range': (0.6, 1.0),
    'colsample_bytree_range': (0.6, 1.0),
    'gamma_range': (0, 5),
    'reg_alpha_range': (0, 10),
    'reg_lambda_range': (0, 10),
}

# ==================== OPTIMIZATION ====================
OPTUNA_CONFIG = {
    'n_trials': 50,                  # Number of optimization trials (increase for better results)
    'timeout': None,                 # Max time in seconds (None = no limit)
    'n_jobs': 1,                     # Parallel trials (set to -1 for all cores)
    'sampler': 'TPE',                # Options: 'TPE', 'Random', 'Grid'
    'direction': 'maximize',         # Maximize F1-Score
    'metric': 'f1_score',            # Optimization metric
}

# ==================== TRADING LOGIC ====================
TRADING_CONFIG = {
    'confidence_threshold': 0.65,    # Probability threshold for signals (0-1)
    'no_trade_range': (0.35, 0.65), # Range for NO TRADE signals
    'risk_per_trade': 0.02,          # 2% risk per trade
    'atr_multiplier': 2.0,           # Stop loss = ATR * multiplier
}

# ==================== VALIDATION ====================
VALIDATION_CONFIG = {
    'cv_splits': 5,                  # Time Series Cross-Validation splits
    'test_size': 0.2,                # Test set size (20%)
    'train_val_split': 0.8,          # Train/validation split for Optuna
}

# ==================== OUTPUT ====================
OUTPUT_CONFIG = {
    'model_save_path': 'models/',    # Directory to save trained models
    'results_save_path': 'results/', # Directory to save results
    'feature_importance_top_n': 20,  # Top N features to display
    'verbosity': 1,                  # 0=silent, 1=normal, 2=debug
}

# ==================== ADVANCED OPTIONS ====================
ADVANCED_CONFIG = {
    'use_gpu': False,                # Use GPU for XGBoost (requires CUDA)
    'early_stopping_rounds': 50,     # Early stopping for training
    'scale_features': True,          # Standardize features
    'remove_outliers': False,        # Remove outliers using IQR method
    'outlier_threshold': 3.0,        # Z-score threshold for outliers
}

# ==================== PRESET CONFIGURATIONS ====================

# Quick Test (Fast, lower accuracy)
PRESET_QUICK = {
    'n_candles': 10000,
    'n_trials': 10,
    'cv_splits': 3,
}

# Balanced (Default)
PRESET_BALANCED = {
    'n_candles': 50000,
    'n_trials': 50,
    'cv_splits': 5,
}

# Production (Slow, highest accuracy)
PRESET_PRODUCTION = {
    'n_candles': 100000,
    'n_trials': 100,
    'cv_splits': 10,
}

# Conservative Trading (Higher precision, fewer trades)
PRESET_CONSERVATIVE = {
    'confidence_threshold': 0.75,
    'no_trade_range': (0.25, 0.75),
    'risk_per_trade': 0.01,
}

# Aggressive Trading (More trades, lower precision)
PRESET_AGGRESSIVE = {
    'confidence_threshold': 0.60,
    'no_trade_range': (0.40, 0.60),
    'risk_per_trade': 0.03,
}

def get_preset(preset_name):
    """
    Get a preset configuration
    
    Args:
        preset_name (str): Name of preset ('quick', 'balanced', 'production', 
                          'conservative', 'aggressive')
    
    Returns:
        dict: Preset configuration
    """
    presets = {
        'quick': PRESET_QUICK,
        'balanced': PRESET_BALANCED,
        'production': PRESET_PRODUCTION,
        'conservative': PRESET_CONSERVATIVE,
        'aggressive': PRESET_AGGRESSIVE,
    }
    
    return presets.get(preset_name.lower(), PRESET_BALANCED)

def apply_preset(preset_name):
    """
    Apply a preset configuration to the global config
    
    Args:
        preset_name (str): Name of preset
    """
    preset = get_preset(preset_name)
    
    # Update relevant configs
    for key, value in preset.items():
        if key in MT5_CONFIG:
            MT5_CONFIG[key] = value
        elif key in OPTUNA_CONFIG:
            OPTUNA_CONFIG[key] = value
        elif key in VALIDATION_CONFIG:
            VALIDATION_CONFIG[key] = value
        elif key in TRADING_CONFIG:
            TRADING_CONFIG[key] = value
    
    print(f"✅ Applied preset: {preset_name.upper()}")
    print(f"   Configuration: {preset}")
