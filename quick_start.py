"""
Quick Start Script for Gold Trading ML Pipeline

This script provides an easy way to run the pipeline with different presets.
"""

import sys
from gold_trading_ml_pipeline import GoldTradingMLPipeline
from config import *
import MetaTrader5 as mt5

def print_banner():
    """Print welcome banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🏆 GOLD TRADING ML SYSTEM - QUICK START 🏆                 ║
    ║                                                               ║
    ║   Select a preset configuration to begin:                    ║
    ║                                                               ║
    ║   1. QUICK TEST    - Fast test (10k candles, 10 trials)     ║
    ║   2. BALANCED      - Default (50k candles, 50 trials)       ║
    ║   3. PRODUCTION    - Best accuracy (100k, 100 trials)       ║
    ║   4. CUSTOM        - Manual configuration                    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

def get_timeframe_constant(timeframe_str):
    """Convert timeframe string to MT5 constant"""
    timeframes = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
    }
    return timeframes.get(timeframe_str, mt5.TIMEFRAME_M15)

def run_quick_test():
    """Run quick test configuration"""
    print("\n🚀 Running QUICK TEST configuration...\n")
    apply_preset('quick')
    
    pipeline = GoldTradingMLPipeline(
        symbol=MT5_CONFIG['symbol'],
        timeframe=get_timeframe_constant(MT5_CONFIG['timeframe']),
        n_candles=MT5_CONFIG['n_candles']
    )
    
    results = pipeline.run_full_pipeline(
        optimize=True,
        n_trials=OPTUNA_CONFIG['n_trials'],
        cv_splits=VALIDATION_CONFIG['cv_splits']
    )
    
    return results

def run_balanced():
    """Run balanced configuration (default)"""
    print("\n🚀 Running BALANCED configuration...\n")
    apply_preset('balanced')
    
    pipeline = GoldTradingMLPipeline(
        symbol=MT5_CONFIG['symbol'],
        timeframe=get_timeframe_constant(MT5_CONFIG['timeframe']),
        n_candles=MT5_CONFIG['n_candles']
    )
    
    results = pipeline.run_full_pipeline(
        optimize=True,
        n_trials=OPTUNA_CONFIG['n_trials'],
        cv_splits=VALIDATION_CONFIG['cv_splits']
    )
    
    return results

def run_production():
    """Run production configuration"""
    print("\n🚀 Running PRODUCTION configuration...\n")
    print("⚠️  WARNING: This will take ~45-60 minutes to complete!")
    confirm = input("   Continue? (y/n): ")
    
    if confirm.lower() != 'y':
        print("❌ Cancelled")
        return None
    
    apply_preset('production')
    
    pipeline = GoldTradingMLPipeline(
        symbol=MT5_CONFIG['symbol'],
        timeframe=get_timeframe_constant(MT5_CONFIG['timeframe']),
        n_candles=MT5_CONFIG['n_candles']
    )
    
    results = pipeline.run_full_pipeline(
        optimize=True,
        n_trials=OPTUNA_CONFIG['n_trials'],
        cv_splits=VALIDATION_CONFIG['cv_splits']
    )
    
    return results

def run_custom():
    """Run with custom configuration"""
    print("\n🔧 Custom Configuration\n")
    
    # Get user inputs
    symbol = input(f"Symbol [{MT5_CONFIG['symbol']}]: ") or MT5_CONFIG['symbol']
    
    print("\nTimeframe options: M1, M5, M15, M30, H1, H4, D1")
    timeframe = input(f"Timeframe [{MT5_CONFIG['timeframe']}]: ") or MT5_CONFIG['timeframe']
    
    n_candles = input(f"Number of candles [{MT5_CONFIG['n_candles']}]: ")
    n_candles = int(n_candles) if n_candles else MT5_CONFIG['n_candles']
    
    n_trials = input(f"Optuna trials [{OPTUNA_CONFIG['n_trials']}]: ")
    n_trials = int(n_trials) if n_trials else OPTUNA_CONFIG['n_trials']
    
    cv_splits = input(f"CV splits [{VALIDATION_CONFIG['cv_splits']}]: ")
    cv_splits = int(cv_splits) if cv_splits else VALIDATION_CONFIG['cv_splits']
    
    threshold = input(f"Confidence threshold [{TRADING_CONFIG['confidence_threshold']}]: ")
    threshold = float(threshold) if threshold else TRADING_CONFIG['confidence_threshold']
    
    print(f"\n📋 Configuration Summary:")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Candles: {n_candles}")
    print(f"   Optuna Trials: {n_trials}")
    print(f"   CV Splits: {cv_splits}")
    print(f"   Threshold: {threshold}")
    
    confirm = input("\nProceed? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled")
        return None
    
    # Run pipeline
    pipeline = GoldTradingMLPipeline(
        symbol=symbol,
        timeframe=get_timeframe_constant(timeframe),
        n_candles=n_candles
    )
    
    results = pipeline.run_full_pipeline(
        optimize=True,
        n_trials=n_trials,
        cv_splits=cv_splits
    )
    
    return results

def main():
    """Main execution"""
    print_banner()
    
    # Get user choice
    choice = input("Select option (1-4): ").strip()
    
    results = None
    
    if choice == '1':
        results = run_quick_test()
    elif choice == '2':
        results = run_balanced()
    elif choice == '3':
        results = run_production()
    elif choice == '4':
        results = run_custom()
    else:
        print("❌ Invalid choice. Running BALANCED configuration by default.")
        results = run_balanced()
    
    # Final summary
    if results is not None:
        print("\n" + "="*60)
        print("🎉 EXECUTION COMPLETE!")
        print("="*60)
        print(f"\n✅ Model trained successfully")
        print(f"📊 CV Results:")
        print(f"   Avg Precision: {results['cv_results']['precision']}")
        print(f"   Avg F1-Score:  {results['cv_results']['f1']}")
        print(f"\n💡 Next Steps:")
        print(f"   - Review feature importance in the output above")
        print(f"   - Test model on live data (see README.md)")
        print(f"   - Adjust confidence threshold if needed")
        print(f"   - Implement risk management rules")
        
        # Save model (optional)
        save_model = input("\n💾 Save model to disk? (y/n): ")
        if save_model.lower() == 'y':
            import pickle
            import os
            
            os.makedirs(OUTPUT_CONFIG['model_save_path'], exist_ok=True)
            
            model_path = os.path.join(
                OUTPUT_CONFIG['model_save_path'],
                f"xgboost_gold_{MT5_CONFIG['symbol']}_{MT5_CONFIG['timeframe']}.pkl"
            )
            
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': results['model'],
                    'scaler': results['scaler'],
                    'feature_columns': results['feature_columns'],
                    'best_params': results['best_params'],
                }, f)
            
            print(f"✅ Model saved to: {model_path}")
    else:
        print("\n❌ Pipeline execution failed or was cancelled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
