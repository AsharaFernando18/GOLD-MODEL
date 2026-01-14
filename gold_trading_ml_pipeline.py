"""
State-of-the-Art Machine Learning Model for Gold (XAUUSD) Trading
Lead AI Quant Researcher - High-Frequency Trading System

This pipeline implements:
- MT5 Integration with USD Index correlation
- Advanced Feature Engineering (Cyclical Time, Volatility Regime, Lag Features)
- XGBoost with Optuna Hyperparameter Tuning
- Probability Thresholding for Signal Generation
- Time Series Cross-Validation with Precision & F1-Score

Author: Lead AI Quant Researcher
Date: January 2026
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Machine Learning & Optimization
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import precision_score, f1_score, accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import optuna
from optuna.samplers import TPESampler

# Technical Analysis
import ta
from ta.trend import EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator


class GoldTradingMLPipeline:
    """
    Production-Grade Machine Learning Pipeline for Gold Trading
    """
    
    def __init__(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M15, n_candles=50000):
        self.symbol = symbol
        self.timeframe = timeframe
        self.n_candles = n_candles
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.best_params = None
        
    def initialize_mt5(self):
        """
        Initialize MetaTrader 5 connection with error handling
        """
        if not mt5.initialize():
            print(f"❌ MT5 initialization failed, error code: {mt5.last_error()}")
            return False
        
        print(f"✅ MT5 initialized successfully")
        print(f"📊 MT5 Version: {mt5.version()}")
        print(f"🏢 Terminal Info: {mt5.terminal_info()}")
        return True
    
    def fetch_mt5_data(self, symbol, timeframe, n_candles):
        """
        Fetch historical data from MetaTrader 5
        
        Args:
            symbol (str): Trading symbol (e.g., 'XAUUSD')
            timeframe: MT5 timeframe constant
            n_candles (int): Number of candles to fetch
            
        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        print(f"\n📥 Fetching {n_candles} candles for {symbol}...")
        
        # Fetch rates
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)
        
        if rates is None or len(rates) == 0:
            print(f"❌ Failed to fetch data for {symbol}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        
        print(f"✅ Fetched {len(df)} candles for {symbol}")
        print(f"📅 Date Range: {df.index[0]} to {df.index[-1]}")
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    def fetch_usd_index(self, start_date, end_date):
        """
        Smart USD Index fetching with MT5 fallback to yfinance
        
        Args:
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            pd.DataFrame: USD Index data
        """
        print(f"\n💵 Attempting to fetch USD Index data...")
        
        # Try MT5 first (DXY or USDX symbols)
        usd_symbols = ['USDX', 'DXY', 'USDDX']
        
        for usd_symbol in usd_symbols:
            print(f"🔍 Trying MT5 symbol: {usd_symbol}")
            usd_data = self.fetch_mt5_data(usd_symbol, self.timeframe, self.n_candles)
            if usd_data is not None:
                print(f"✅ Successfully fetched {usd_symbol} from MT5")
                return usd_data
        
        # Fallback to yfinance
        print(f"⚠️ USD Index not found in MT5, falling back to yfinance (DX-Y.NYB)...")
        try:
            usd_df = yf.download('DX-Y.NYB', start=start_date, end=end_date, interval='15m', progress=False)
            if not usd_df.empty:
                print(f"✅ Fetched USD Index from yfinance: {len(usd_df)} records")
                return usd_df[['Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception as e:
            print(f"⚠️ yfinance fetch failed: {e}")
        
        print(f"⚠️ Could not fetch USD Index data, will proceed without it")
        return None
    
    def merge_usd_correlation(self, gold_df, usd_df):
        """
        Merge USD Index with Gold data based on timestamps
        
        Args:
            gold_df: Gold OHLCV DataFrame
            usd_df: USD Index OHLCV DataFrame
            
        Returns:
            pd.DataFrame: Merged dataframe
        """
        if usd_df is None:
            print("⚠️ No USD Index data to merge")
            return gold_df
        
        print(f"\n🔗 Merging Gold and USD Index data...")
        
        # Rename USD columns
        usd_df = usd_df.add_prefix('USD_')
        
        # Merge on index (timestamp)
        merged_df = gold_df.join(usd_df, how='left')
        
        # Forward fill missing USD values (for timezone mismatches)
        merged_df.fillna(method='ffill', inplace=True)
        
        print(f"✅ Merged data shape: {merged_df.shape}")
        return merged_df
    
    def create_advanced_features(self, df):
        """
        Advanced Feature Engineering - The "Brain" of the Model
        
        Features:
        1. Cyclical Time Features (Hour, Day of Week)
        2. Volatility Regime (ATR, BB Width)
        3. Lag Features (Returns t-1, t-2, t-3)
        4. Interaction Features (Close/EMA ratio)
        5. Technical Indicators (RSI, Stochastic, ADX)
        6. USD Correlation Features
        """
        print(f"\n🧠 Engineering Advanced Features...")
        
        df = df.copy()
        
        # ==================== 1. CYCLICAL TIME FEATURES ====================
        print("⏰ Creating cyclical time features...")
        df['Hour'] = df.index.hour
        df['DayOfWeek'] = df.index.dayofweek
        
        # Sine/Cosine transformation to capture cyclical nature
        df['Hour_Sin'] = np.sin(2 * np.pi * df['Hour'] / 24)
        df['Hour_Cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
        df['DayOfWeek_Sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 7)
        df['DayOfWeek_Cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 7)
        
        # ==================== 2. VOLATILITY REGIME ====================
        print("📊 Calculating volatility regime indicators...")
        
        # ATR (Average True Range)
        atr_indicator = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ATR'] = atr_indicator.average_true_range()
        
        # Bollinger Bands Width (volatility measure)
        bb_indicator = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_Width'] = bb_indicator.bollinger_wband()
        df['BB_High'] = bb_indicator.bollinger_hband()
        df['BB_Low'] = bb_indicator.bollinger_lband()
        df['BB_Mid'] = bb_indicator.bollinger_mavg()
        
        # Volatility Regime Classification
        df['Volatility_Regime'] = np.where(df['ATR'] > df['ATR'].rolling(50).mean(), 1, 0)  # 1=High Vol, 0=Low Vol
        
        # ==================== 3. LAG FEATURES (Momentum) ====================
        print("🔄 Creating lag features for momentum...")
        
        # Returns
        df['Returns'] = df['Close'].pct_change()
        df['Returns_t1'] = df['Returns'].shift(1)
        df['Returns_t2'] = df['Returns'].shift(2)
        df['Returns_t3'] = df['Returns'].shift(3)
        
        # Price lags
        df['Close_t1'] = df['Close'].shift(1)
        df['Close_t2'] = df['Close'].shift(2)
        
        # Volume momentum
        df['Volume_MA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / (df['Volume_MA'] + 1e-8)
        
        # ==================== 4. TECHNICAL INDICATORS ====================
        print("📈 Calculating technical indicators...")
        
        # EMAs
        df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
        df['EMA_200'] = EMAIndicator(close=df['Close'], window=200).ema_indicator()
        
        # RSI
        rsi_indicator = RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi_indicator.rsi()
        
        # Stochastic Oscillator
        stoch_indicator = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=14, smooth_window=3)
        df['Stoch_K'] = stoch_indicator.stoch()
        df['Stoch_D'] = stoch_indicator.stoch_signal()
        
        # ADX (Trend Strength)
        adx_indicator = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX'] = adx_indicator.adx()
        
        # MACD
        df['EMA_12'] = EMAIndicator(close=df['Close'], window=12).ema_indicator()
        df['EMA_26'] = EMAIndicator(close=df['Close'], window=26).ema_indicator()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].rolling(9).mean()
        df['MACD_Diff'] = df['MACD'] - df['MACD_Signal']
        
        # ==================== 5. INTERACTION FEATURES ====================
        print("🔗 Creating interaction features...")
        
        # Price relative to EMAs
        df['Close_EMA20_Ratio'] = df['Close'] / (df['EMA_20'] + 1e-8)
        df['Close_EMA50_Ratio'] = df['Close'] / (df['EMA_50'] + 1e-8)
        df['Close_EMA200_Ratio'] = df['Close'] / (df['EMA_200'] + 1e-8)
        
        # Price position in Bollinger Bands
        df['BB_Position'] = (df['Close'] - df['BB_Low']) / (df['BB_High'] - df['BB_Low'] + 1e-8)
        
        # ==================== 6. USD CORRELATION FEATURES ====================
        if 'USD_Close' in df.columns:
            print("💵 Creating USD correlation features...")
            df['USD_Returns'] = df['USD_Close'].pct_change()
            df['USD_EMA_20'] = EMAIndicator(close=df['USD_Close'], window=20).ema_indicator()
            df['Gold_USD_Ratio'] = df['Close'] / (df['USD_Close'] + 1e-8)
            df['Gold_USD_Correlation'] = df['Returns'].rolling(50).corr(df['USD_Returns'])
        
        # ==================== 7. TARGET VARIABLE (Forward Returns) ====================
        print("🎯 Creating target variable...")
        
        # Define target: 1 if next candle closes higher, 0 otherwise
        df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
        
        # Alternative: Use forward returns for threshold-based labeling
        df['Forward_Returns'] = df['Close'].shift(-1) / df['Close'] - 1
        
        # Clean data
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)
        
        print(f"✅ Feature engineering complete. Shape: {df.shape}")
        print(f"📊 Features created: {df.shape[1]} columns")
        
        return df
    
    def prepare_features_and_target(self, df):
        """
        Prepare feature matrix (X) and target vector (y)
        """
        print(f"\n🔧 Preparing feature matrix and target vector...")
        
        # Exclude non-feature columns
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Forward_Returns',
                       'Hour', 'DayOfWeek', 'USD_Open', 'USD_High', 'USD_Low', 'USD_Close', 'USD_Volume']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y = df['Target']
        
        self.feature_columns = feature_cols
        
        print(f"✅ Features prepared: {X.shape}")
        print(f"📋 Feature columns ({len(feature_cols)}): {feature_cols[:10]}...")
        print(f"🎯 Target distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def objective(self, trial, X_train, y_train, X_val, y_val):
        """
        Optuna objective function for hyperparameter tuning
        """
        # Suggest hyperparameters
        params = {
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=100),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42,
            'tree_method': 'hist'
        }
        
        # Train model
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        
        # Predict
        y_pred = model.predict(X_val)
        
        # Return F1-Score (optimize for precision and recall balance)
        f1 = f1_score(y_val, y_pred)
        
        return f1
    
    def optimize_hyperparameters(self, X_train, y_train, X_val, y_val, n_trials=50):
        """
        Optimize hyperparameters using Optuna
        """
        print(f"\n🔍 Starting Hyperparameter Optimization with Optuna ({n_trials} trials)...")
        
        # Create study
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        
        # Optimize
        study.optimize(
            lambda trial: self.objective(trial, X_train, y_train, X_val, y_val),
            n_trials=n_trials,
            show_progress_bar=True
        )
        
        print(f"\n✅ Optimization complete!")
        print(f"🏆 Best F1-Score: {study.best_value:.4f}")
        print(f"⚙️ Best Parameters:")
        for key, value in study.best_params.items():
            print(f"   {key}: {value}")
        
        self.best_params = study.best_params
        
        return study.best_params
    
    def train_model(self, X_train, y_train, params=None):
        """
        Train XGBoost model with optimized parameters
        """
        print(f"\n🎓 Training XGBoost Model...")
        
        if params is None:
            params = self.best_params
        
        # Add fixed parameters
        params.update({
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42,
            'tree_method': 'hist'
        })
        
        # Train model
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X_train, y_train, verbose=True)
        
        print(f"✅ Model training complete!")
        
        return self.model
    
    def evaluate_model(self, X_test, y_test, threshold=0.65):
        """
        Evaluate model with probability thresholding
        
        Args:
            X_test: Test features
            y_test: Test target
            threshold: Confidence threshold for trading signals
        """
        print(f"\n📊 Evaluating Model Performance...")
        
        # Get probability predictions
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Standard predictions
        y_pred_standard = self.model.predict(X_test)
        
        # Smart probability thresholding
        y_pred_smart = np.where(y_proba > threshold, 1,
                               np.where(y_proba < (1 - threshold), 0, -1))  # -1 = NO TRADE
        
        # Filter out NO TRADE signals for evaluation
        valid_indices = y_pred_smart != -1
        y_test_filtered = y_test[valid_indices]
        y_pred_filtered = y_pred_smart[valid_indices]
        
        # Calculate metrics
        print(f"\n{'='*60}")
        print(f"STANDARD PREDICTIONS (No Thresholding)")
        print(f"{'='*60}")
        print(f"Accuracy:  {accuracy_score(y_test, y_pred_standard):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred_standard):.4f}")
        print(f"F1-Score:  {f1_score(y_test, y_pred_standard):.4f}")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred_standard))
        
        print(f"\n{'='*60}")
        print(f"SMART PREDICTIONS (Threshold: {threshold*100:.0f}%)")
        print(f"{'='*60}")
        print(f"Total Predictions: {len(y_test)}")
        print(f"Traded Signals:    {valid_indices.sum()} ({valid_indices.sum()/len(y_test)*100:.1f}%)")
        print(f"NO TRADE Signals:  {(~valid_indices).sum()} ({(~valid_indices).sum()/len(y_test)*100:.1f}%)")
        print(f"\nAccuracy:  {accuracy_score(y_test_filtered, y_pred_filtered):.4f}")
        print(f"Precision: {precision_score(y_test_filtered, y_pred_filtered):.4f} ⭐")
        print(f"F1-Score:  {f1_score(y_test_filtered, y_pred_filtered):.4f} ⭐")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test_filtered, y_pred_filtered))
        
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION REPORT (Smart Predictions)")
        print(f"{'='*60}")
        print(classification_report(y_test_filtered, y_pred_filtered, target_names=['SELL', 'BUY']))
        
        # Probability distribution
        print(f"\n{'='*60}")
        print(f"PROBABILITY DISTRIBUTION")
        print(f"{'='*60}")
        print(f"High Confidence BUY (>{threshold*100:.0f}%):   {(y_proba > threshold).sum()} signals")
        print(f"High Confidence SELL (<{(1-threshold)*100:.0f}%): {(y_proba < (1-threshold)).sum()} signals")
        print(f"NO TRADE ({(1-threshold)*100:.0f}%-{threshold*100:.0f}%):          {((y_proba >= (1-threshold)) & (y_proba <= threshold)).sum()} signals")
        
        return {
            'accuracy_standard': accuracy_score(y_test, y_pred_standard),
            'precision_standard': precision_score(y_test, y_pred_standard),
            'f1_standard': f1_score(y_test, y_pred_standard),
            'accuracy_smart': accuracy_score(y_test_filtered, y_pred_filtered),
            'precision_smart': precision_score(y_test_filtered, y_pred_filtered),
            'f1_smart': f1_score(y_test_filtered, y_pred_filtered),
            'trade_percentage': valid_indices.sum() / len(y_test) * 100
        }
    
    def time_series_cross_validation(self, X, y, n_splits=5, optimize=True, n_trials=30):
        """
        Robust Time Series Cross-Validation
        
        Args:
            X: Feature matrix
            y: Target vector
            n_splits: Number of time series splits
            optimize: Whether to optimize hyperparameters
            n_trials: Number of Optuna trials
        """
        print(f"\n{'='*60}")
        print(f"TIME SERIES CROSS-VALIDATION ({n_splits} Splits)")
        print(f"{'='*60}")
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        results = {
            'accuracy': [],
            'precision': [],
            'f1': []
        }
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
            print(f"\n{'─'*60}")
            print(f"FOLD {fold}/{n_splits}")
            print(f"{'─'*60}")
            
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Convert back to DataFrame
            X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
            X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
            
            # Optimize hyperparameters on first fold
            if fold == 1 and optimize:
                # Use 80-20 split of training data for optimization
                split_point = int(len(X_train_scaled) * 0.8)
                X_train_opt = X_train_scaled.iloc[:split_point]
                y_train_opt = y_train.iloc[:split_point]
                X_val_opt = X_train_scaled.iloc[split_point:]
                y_val_opt = y_train.iloc[split_point:]
                
                best_params = self.optimize_hyperparameters(X_train_opt, y_train_opt, X_val_opt, y_val_opt, n_trials=n_trials)
            
            # Train model
            self.train_model(X_train_scaled, y_train, params=self.best_params if optimize else None)
            
            # Evaluate
            metrics = self.evaluate_model(X_test_scaled, y_test, threshold=0.65)
            
            results['accuracy'].append(metrics['accuracy_smart'])
            results['precision'].append(metrics['precision_smart'])
            results['f1'].append(metrics['f1_smart'])
        
        # Summary
        print(f"\n{'='*60}")
        print(f"CROSS-VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Average Accuracy:  {np.mean(results['accuracy']):.4f} ± {np.std(results['accuracy']):.4f}")
        print(f"Average Precision: {np.mean(results['precision']):.4f} ± {np.std(results['precision']):.4f} ⭐")
        print(f"Average F1-Score:  {np.mean(results['f1']):.4f} ± {np.std(results['f1']):.4f} ⭐")
        
        return results
    
    def generate_trading_signal(self, current_data, threshold=0.65):
        """
        Generate trading signal with probability thresholding
        
        Args:
            current_data: Current market data (single row DataFrame)
            threshold: Confidence threshold
            
        Returns:
            dict: Signal information
        """
        # Scale features
        current_scaled = self.scaler.transform(current_data[self.feature_columns])
        
        # Get probability
        proba = self.model.predict_proba(current_scaled)[0, 1]
        
        # Generate signal
        if proba > threshold:
            signal = "BUY"
            confidence = proba
        elif proba < (1 - threshold):
            signal = "SELL"
            confidence = 1 - proba
        else:
            signal = "NO TRADE"
            confidence = max(proba, 1 - proba)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_probability': proba,
            'sell_probability': 1 - proba
        }
    
    def run_full_pipeline(self, optimize=True, n_trials=50, cv_splits=5):
        """
        Execute the complete ML pipeline
        
        Args:
            optimize: Whether to run Optuna optimization
            n_trials: Number of Optuna trials
            cv_splits: Number of CV splits
        """
        print(f"\n{'='*60}")
        print(f"🚀 GOLD TRADING ML PIPELINE - EXECUTION START")
        print(f"{'='*60}")
        
        # Step 1: Initialize MT5
        if not self.initialize_mt5():
            return None
        
        # Step 2: Fetch Gold data
        gold_df = self.fetch_mt5_data(self.symbol, self.timeframe, self.n_candles)
        if gold_df is None:
            return None
        
        # Step 3: Fetch USD Index
        start_date = gold_df.index[0]
        end_date = gold_df.index[-1]
        usd_df = self.fetch_usd_index(start_date, end_date)
        
        # Step 4: Merge data
        merged_df = self.merge_usd_correlation(gold_df, usd_df)
        
        # Step 5: Feature Engineering
        df_features = self.create_advanced_features(merged_df)
        
        # Step 6: Prepare X and y
        X, y = self.prepare_features_and_target(df_features)
        
        # Step 7: Time Series Cross-Validation
        cv_results = self.time_series_cross_validation(X, y, n_splits=cv_splits, optimize=optimize, n_trials=n_trials)
        
        # Step 8: Final Model Training (on all data)
        print(f"\n{'='*60}")
        print(f"FINAL MODEL TRAINING (Full Dataset)")
        print(f"{'='*60}")
        
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        self.train_model(X_scaled, y, params=self.best_params)
        
        # Feature Importance
        print(f"\n{'='*60}")
        print(f"TOP 20 FEATURE IMPORTANCE")
        print(f"{'='*60}")
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(20).to_string(index=False))
        
        # Shutdown MT5
        mt5.shutdown()
        print(f"\n✅ MT5 connection closed")
        
        print(f"\n{'='*60}")
        print(f"🎉 PIPELINE EXECUTION COMPLETE")
        print(f"{'='*60}")
        
        return {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'best_params': self.best_params,
            'cv_results': cv_results,
            'feature_importance': feature_importance
        }


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    """
    Main execution block
    """
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🏆 STATE-OF-THE-ART GOLD TRADING ML SYSTEM 🏆              ║
    ║                                                               ║
    ║   Lead AI Quant Researcher - HFT Division                    ║
    ║   Symbol: XAUUSD | Timeframe: M15 | ML: XGBoost + Optuna    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        n_candles=50000
    )
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(
        optimize=True,      # Enable Optuna optimization
        n_trials=50,        # Number of Optuna trials (increase for better results)
        cv_splits=5         # Time Series CV splits
    )
    
    # Example: Generate live signal (uncomment when needed)
    """
    # For live trading, fetch latest data and generate signal
    if results is not None:
        print(f"\n{'='*60}")
        print(f"LIVE SIGNAL GENERATION EXAMPLE")
        print(f"{'='*60}")
        
        # Fetch latest candle
        latest_data = pipeline.fetch_mt5_data("XAUUSD", mt5.TIMEFRAME_M15, 300)
        if latest_data is not None:
            # Apply same feature engineering
            latest_features = pipeline.create_advanced_features(latest_data)
            
            # Generate signal for latest candle
            signal_info = pipeline.generate_trading_signal(latest_features.iloc[[-1]], threshold=0.65)
            
            print(f"\n🎯 TRADING SIGNAL:")
            print(f"   Signal:       {signal_info['signal']}")
            print(f"   Confidence:   {signal_info['confidence']*100:.2f}%")
            print(f"   Buy Prob:     {signal_info['buy_probability']*100:.2f}%")
            print(f"   Sell Prob:    {signal_info['sell_probability']*100:.2f}%")
    """
    
    print(f"\n✅ All operations completed successfully!")
