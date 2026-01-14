"""
Example Usage Script - Gold Trading ML Pipeline

This script demonstrates various ways to use the pipeline
"""

from gold_trading_ml_pipeline import GoldTradingMLPipeline
from evaluation_utils import TradingBacktest
import MetaTrader5 as mt5
import pandas as pd


def example_1_basic_training():
    """
    Example 1: Basic model training with default settings
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: BASIC TRAINING")
    print("="*60)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        n_candles=20000  # Use smaller dataset for quick test
    )
    
    # Run pipeline with optimization
    results = pipeline.run_full_pipeline(
        optimize=True,
        n_trials=20,  # Quick optimization
        cv_splits=3
    )
    
    print("\n✅ Example 1 complete!")
    return pipeline, results


def example_2_custom_threshold():
    """
    Example 2: Training with custom confidence threshold
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: CUSTOM THRESHOLD")
    print("="*60)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        n_candles=20000
    )
    
    # Initialize MT5 and fetch data
    if not pipeline.initialize_mt5():
        return None, None
    
    gold_df = pipeline.fetch_mt5_data(pipeline.symbol, pipeline.timeframe, pipeline.n_candles)
    
    # Feature engineering
    df_features = pipeline.create_advanced_features(gold_df)
    X, y = pipeline.prepare_features_and_target(df_features)
    
    # Scale features
    X_scaled = pd.DataFrame(
        pipeline.scaler.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    # Train model (skip optimization for speed)
    pipeline.best_params = {
        'learning_rate': 0.1,
        'max_depth': 6,
        'n_estimators': 300,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 1,
        'reg_alpha': 1,
        'reg_lambda': 1,
    }
    
    pipeline.train_model(X_scaled, y)
    
    # Test different thresholds
    print("\n" + "="*60)
    print("TESTING DIFFERENT THRESHOLDS")
    print("="*60)
    
    for threshold in [0.60, 0.65, 0.70, 0.75]:
        print(f"\n--- Threshold: {threshold*100:.0f}% ---")
        metrics = pipeline.evaluate_model(X_scaled, y, threshold=threshold)
    
    mt5.shutdown()
    print("\n✅ Example 2 complete!")
    return pipeline, None


def example_3_live_signals():
    """
    Example 3: Generate live trading signals
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: LIVE SIGNAL GENERATION")
    print("="*60)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        n_candles=10000
    )
    
    # Quick training
    if not pipeline.initialize_mt5():
        return None
    
    gold_df = pipeline.fetch_mt5_data(pipeline.symbol, pipeline.timeframe, pipeline.n_candles)
    df_features = pipeline.create_advanced_features(gold_df)
    X, y = pipeline.prepare_features_and_target(df_features)
    
    X_scaled = pd.DataFrame(
        pipeline.scaler.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    # Use default params for speed
    pipeline.best_params = {
        'learning_rate': 0.1,
        'max_depth': 6,
        'n_estimators': 300,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 1,
        'reg_alpha': 1,
        'reg_lambda': 1,
    }
    
    pipeline.train_model(X_scaled, y)
    
    # Fetch latest data
    print("\n" + "="*60)
    print("GENERATING LIVE SIGNALS")
    print("="*60)
    
    latest_data = pipeline.fetch_mt5_data("XAUUSD", mt5.TIMEFRAME_M15, 500)
    latest_features = pipeline.create_advanced_features(latest_data)
    
    # Generate signals for last 10 candles
    for i in range(-10, 0):
        signal_info = pipeline.generate_trading_signal(
            latest_features.iloc[[i]], 
            threshold=0.65
        )
        
        timestamp = latest_features.index[i]
        price = latest_features['Close'].iloc[i]
        
        print(f"\n📅 {timestamp}")
        print(f"   Price:        ${price:.2f}")
        print(f"   Signal:       {signal_info['signal']}")
        print(f"   Confidence:   {signal_info['confidence']*100:.2f}%")
        print(f"   Buy Prob:     {signal_info['buy_probability']*100:.2f}%")
        print(f"   Sell Prob:    {signal_info['sell_probability']*100:.2f}%")
    
    mt5.shutdown()
    print("\n✅ Example 3 complete!")
    return pipeline


def example_4_backtesting():
    """
    Example 4: Backtest the strategy
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: BACKTESTING")
    print("="*60)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        n_candles=10000
    )
    
    # Quick training
    if not pipeline.initialize_mt5():
        return None
    
    gold_df = pipeline.fetch_mt5_data(pipeline.symbol, pipeline.timeframe, pipeline.n_candles)
    df_features = pipeline.create_advanced_features(gold_df)
    X, y = pipeline.prepare_features_and_target(df_features)
    
    X_scaled = pd.DataFrame(
        pipeline.scaler.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    # Train model
    pipeline.best_params = {
        'learning_rate': 0.1,
        'max_depth': 6,
        'n_estimators': 300,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 1,
        'reg_alpha': 1,
        'reg_lambda': 1,
    }
    
    pipeline.train_model(X_scaled, y)
    
    # Generate signals
    y_proba = pipeline.model.predict_proba(X_scaled)[:, 1]
    signals = np.where(y_proba > 0.65, 1,
                      np.where(y_proba < 0.35, 0, -1))
    
    # Get prices and ATR
    prices = df_features['Close'].values
    atr_values = df_features['ATR'].values
    
    # Run backtest
    backtester = TradingBacktest(
        initial_balance=10000,
        risk_per_trade=0.02,
        atr_multiplier=2.0
    )
    
    results = backtester.run_backtest(df_features, signals, prices, atr_values)
    
    # Plot equity curve
    backtester.plot_equity_curve(save_path='equity_curve.png')
    
    # Export trades
    backtester.export_trades('trades.csv')
    
    mt5.shutdown()
    print("\n✅ Example 4 complete!")
    return backtester


def example_5_different_timeframes():
    """
    Example 5: Compare different timeframes
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: MULTI-TIMEFRAME COMPARISON")
    print("="*60)
    
    timeframes = {
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'H1': mt5.TIMEFRAME_H1,
    }
    
    results_comparison = {}
    
    for tf_name, tf_constant in timeframes.items():
        print(f"\n{'─'*60}")
        print(f"Testing Timeframe: {tf_name}")
        print(f"{'─'*60}")
        
        pipeline = GoldTradingMLPipeline(
            symbol="XAUUSD",
            timeframe=tf_constant,
            n_candles=5000  # Smaller for speed
        )
        
        if not pipeline.initialize_mt5():
            continue
        
        gold_df = pipeline.fetch_mt5_data(pipeline.symbol, pipeline.timeframe, pipeline.n_candles)
        
        if gold_df is None:
            mt5.shutdown()
            continue
        
        df_features = pipeline.create_advanced_features(gold_df)
        X, y = pipeline.prepare_features_and_target(df_features)
        
        X_scaled = pd.DataFrame(
            pipeline.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        # Quick train
        pipeline.best_params = {
            'learning_rate': 0.1,
            'max_depth': 6,
            'n_estimators': 200,
            'min_child_weight': 3,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 1,
            'reg_alpha': 1,
            'reg_lambda': 1,
        }
        
        pipeline.train_model(X_scaled, y)
        metrics = pipeline.evaluate_model(X_scaled, y, threshold=0.65)
        
        results_comparison[tf_name] = metrics
        
        mt5.shutdown()
    
    # Summary
    print("\n" + "="*60)
    print("TIMEFRAME COMPARISON SUMMARY")
    print("="*60)
    
    for tf_name, metrics in results_comparison.items():
        print(f"\n{tf_name}:")
        print(f"  Precision: {metrics['precision_smart']:.4f}")
        print(f"  F1-Score:  {metrics['f1_smart']:.4f}")
        print(f"  Trade %:   {metrics['trade_percentage']:.1f}%")
    
    print("\n✅ Example 5 complete!")
    return results_comparison


def main():
    """
    Main menu for examples
    """
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   📚 GOLD TRADING ML - EXAMPLE USAGE 📚                      ║
    ║                                                               ║
    ║   Select an example to run:                                  ║
    ║                                                               ║
    ║   1. Basic Training                                          ║
    ║   2. Custom Threshold Testing                                ║
    ║   3. Live Signal Generation                                  ║
    ║   4. Backtesting                                             ║
    ║   5. Multi-Timeframe Comparison                              ║
    ║   6. Run All Examples                                        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    choice = input("Select option (1-6): ").strip()
    
    if choice == '1':
        example_1_basic_training()
    elif choice == '2':
        example_2_custom_threshold()
    elif choice == '3':
        example_3_live_signals()
    elif choice == '4':
        example_4_backtesting()
    elif choice == '5':
        example_5_different_timeframes()
    elif choice == '6':
        print("\n🚀 Running all examples...\n")
        example_1_basic_training()
        example_2_custom_threshold()
        example_3_live_signals()
        example_4_backtesting()
        example_5_different_timeframes()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
        print("\n" + "="*60)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
