"""
Backtesting Script for Gold Trading ML Pipeline

This script runs a comprehensive backtest on historical data to evaluate
the strategy's performance including returns, Sharpe ratio, and drawdown.
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime
import MetaTrader5 as mt5

print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       🏆 GOLD TRADING BACKTEST ENGINE 🏆                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

# Import custom modules
try:
    from gold_trading_ml_pipeline import GoldTradingMLPipeline
    from evaluation_utils import BacktestEngine
    from config import *
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure all required files are in the same directory.")
    sys.exit(1)

def main():
    """Main backtesting function"""
    
    print("\n📊 Initializing Backtest Engine...")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = GoldTradingMLPipeline(
        symbol=MT5_CONFIG['symbol'],
        timeframe=getattr(mt5, f"TIMEFRAME_{MT5_CONFIG['timeframe']}"),
        n_candles=MT5_CONFIG['n_candles']
    )
    
    # Initialize MT5
    print("\n🔌 Connecting to MetaTrader 5...")
    if not pipeline.initialize_mt5():
        print("❌ Failed to initialize MT5. Running in demo mode with synthetic data...")
        use_mt5_data = False
    else:
        use_mt5_data = True
    
    # Fetch data
    if use_mt5_data:
        print(f"\n📥 Fetching {MT5_CONFIG['n_candles']} candles of {MT5_CONFIG['symbol']} data...")
        data = pipeline.fetch_mt5_data(
            MT5_CONFIG['symbol'],
            getattr(mt5, f"TIMEFRAME_{MT5_CONFIG['timeframe']}"),
            MT5_CONFIG['n_candles']
        )
        
        if data is None:
            print("❌ Failed to fetch data from MT5")
            return
    else:
        # Generate synthetic data for demo
        print("\n📥 Generating synthetic data for demonstration...")
        n_samples = 10000
        np.random.seed(42)
        
        base_price = 1800
        trend = np.linspace(0, 200, n_samples)
        noise = np.random.randn(n_samples) * 15
        prices = base_price + trend + noise
        
        dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='15min')
        data = pd.DataFrame({
            'time': dates,
            'open': prices + np.random.randn(n_samples) * 3,
            'high': prices + abs(np.random.randn(n_samples) * 8),
            'low': prices - abs(np.random.randn(n_samples) * 8),
            'close': prices,
            'tick_volume': np.random.randint(100, 1000, n_samples),
            'real_volume': np.random.randint(1000, 10000, n_samples)
        })
        
        data['high'] = data[['open', 'high', 'close']].max(axis=1)
        data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    print(f"   ✅ Loaded {len(data)} candles")
    print(f"   📅 Date range: {data['time'].min()} to {data['time'].max()}")
    print(f"   💰 Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    # Create features
    print("\n🧠 Creating advanced features...")
    featured_data = pipeline.create_advanced_features(data)
    print(f"   ✅ Created {len(featured_data.columns)} features")
    
    # Train model
    print("\n🤖 Training XGBoost model with Optuna optimization...")
    print("   This may take a few minutes...")
    
    # Use reduced trials for backtest
    original_trials = OPTUNA_CONFIG['n_trials']
    OPTUNA_CONFIG['n_trials'] = 20  # Faster for backtest
    
    pipeline.train_model_with_optuna(featured_data)
    
    OPTUNA_CONFIG['n_trials'] = original_trials  # Restore
    
    # Run backtest
    print("\n📈 Running backtest simulation...")
    print("=" * 70)
    
    backtest = BacktestEngine(
        initial_capital=10000,
        position_size=0.1,  # 10% of capital per trade
        commission=0.0003   # 3 pips commission
    )
    
    # Generate signals for all data
    signals = []
    for i in range(len(featured_data)):
        row = featured_data.iloc[[i]]
        signal_info = pipeline.generate_trading_signal(
            row, 
            threshold=MODEL_CONFIG['probability_threshold']
        )
        signals.append(signal_info)
    
    # Create signals DataFrame
    signals_df = pd.DataFrame(signals)
    signals_df['time'] = featured_data['time'].values
    signals_df['price'] = featured_data['close'].values
    
    # Run backtest
    results = backtest.run_backtest(signals_df)
    
    # Display results
    print("\n" + "=" * 70)
    print(" BACKTEST RESULTS")
    print("=" * 70)
    print()
    
    print(f"📊 Trading Statistics:")
    print(f"   Total Trades:        {results['total_trades']}")
    print(f"   Winning Trades:      {results['winning_trades']} ({results['win_rate']:.2f}%)")
    print(f"   Losing Trades:       {results['losing_trades']}")
    print()
    
    print(f"💰 Financial Performance:")
    print(f"   Initial Capital:     ${results['initial_capital']:,.2f}")
    print(f"   Final Capital:       ${results['final_capital']:,.2f}")
    print(f"   Total Return:        {results['total_return']:.2f}%")
    print(f"   Total Profit:        ${results['total_profit']:,.2f}")
    print()
    
    print(f"📈 Risk Metrics:")
    print(f"   Sharpe Ratio:        {results['sharpe_ratio']:.3f}")
    print(f"   Max Drawdown:        {results['max_drawdown']:.2f}%")
    print(f"   Profit Factor:       {results['profit_factor']:.3f}")
    print()
    
    print(f"🎯 Signal Quality:")
    buy_signals = (signals_df['signal'] == 'BUY').sum()
    sell_signals = (signals_df['signal'] == 'SELL').sum()
    no_trade = (signals_df['signal'] == 'NO_TRADE').sum()
    
    print(f"   Buy Signals:         {buy_signals} ({buy_signals/len(signals_df)*100:.1f}%)")
    print(f"   Sell Signals:        {sell_signals} ({sell_signals/len(signals_df)*100:.1f}%)")
    print(f"   No Trade:            {no_trade} ({no_trade/len(signals_df)*100:.1f}%)")
    print(f"   Avg Confidence:      {signals_df['confidence'].mean()*100:.2f}%")
    print()
    
    # Performance grade
    print("🏆 Performance Grade:")
    if results['sharpe_ratio'] > 2 and results['total_return'] > 50:
        grade = "A+ (EXCELLENT)"
    elif results['sharpe_ratio'] > 1.5 and results['total_return'] > 30:
        grade = "A (VERY GOOD)"
    elif results['sharpe_ratio'] > 1 and results['total_return'] > 15:
        grade = "B (GOOD)"
    elif results['sharpe_ratio'] > 0.5 and results['total_return'] > 0:
        grade = "C (AVERAGE)"
    else:
        grade = "D (NEEDS IMPROVEMENT)"
    
    print(f"   Grade: {grade}")
    print()
    
    print("=" * 70)
    print()
    
    # Save results
    output_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results['trades_df'].to_csv(output_file, index=False)
    print(f"💾 Detailed trade log saved to: {output_file}")
    
    # Cleanup
    if use_mt5_data:
        mt5.shutdown()
    
    print("\n✅ Backtest complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrupted by user")
        mt5.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        sys.exit(1)
