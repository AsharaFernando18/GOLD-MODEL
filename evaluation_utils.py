"""
Model Evaluation and Backtesting Utilities

This module provides tools for:
- Backtesting trading strategies
- Walk-forward analysis
- Performance metrics calculation
- Equity curve visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pickle


class TradingBacktest:
    """
    Backtesting engine for ML trading strategies
    """
    
    def __init__(self, initial_balance=10000, risk_per_trade=0.02, atr_multiplier=2.0):
        """
        Initialize backtester
        
        Args:
            initial_balance (float): Starting capital
            risk_per_trade (float): Risk per trade as fraction of balance
            atr_multiplier (float): Stop loss multiplier for ATR
        """
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier
        self.trades = []
        self.equity_curve = []
        
    def calculate_position_size(self, balance, entry_price, stop_loss_price):
        """
        Calculate position size based on risk management
        
        Args:
            balance (float): Current account balance
            entry_price (float): Entry price
            stop_loss_price (float): Stop loss price
            
        Returns:
            float: Position size in lots
        """
        risk_amount = balance * self.risk_per_trade
        price_difference = abs(entry_price - stop_loss_price)
        
        if price_difference == 0:
            return 0
        
        position_size = risk_amount / price_difference
        return position_size
    
    def run_backtest(self, df, signals, prices, atr_values):
        """
        Execute backtest on historical data
        
        Args:
            df (pd.DataFrame): Historical data with features
            signals (np.array): Trading signals (1=BUY, 0=SELL, -1=NO_TRADE)
            prices (np.array): Entry prices
            atr_values (np.array): ATR values for stop loss
            
        Returns:
            dict: Backtest results
        """
        print("\n" + "="*60)
        print("🔙 RUNNING BACKTEST")
        print("="*60)
        
        balance = self.initial_balance
        position = None
        entry_price = 0
        stop_loss = 0
        take_profit = 0
        
        for i in range(len(signals)):
            if signals[i] == -1:  # NO TRADE
                continue
            
            current_price = prices[i]
            current_atr = atr_values[i]
            
            # Close existing position
            if position is not None:
                # Check stop loss
                if position == 'BUY' and current_price <= stop_loss:
                    pnl = (stop_loss - entry_price) * position_size
                    balance += pnl
                    self.trades.append({
                        'entry_time': df.index[entry_idx],
                        'exit_time': df.index[i],
                        'type': 'BUY',
                        'entry_price': entry_price,
                        'exit_price': stop_loss,
                        'pnl': pnl,
                        'pnl_pct': (pnl / (entry_price * position_size)) * 100,
                        'outcome': 'LOSS'
                    })
                    position = None
                    
                elif position == 'SELL' and current_price >= stop_loss:
                    pnl = (entry_price - stop_loss) * position_size
                    balance += pnl
                    self.trades.append({
                        'entry_time': df.index[entry_idx],
                        'exit_time': df.index[i],
                        'type': 'SELL',
                        'entry_price': entry_price,
                        'exit_price': stop_loss,
                        'pnl': pnl,
                        'pnl_pct': (pnl / (entry_price * position_size)) * 100,
                        'outcome': 'LOSS'
                    })
                    position = None
                
                # Check take profit
                elif position == 'BUY' and current_price >= take_profit:
                    pnl = (take_profit - entry_price) * position_size
                    balance += pnl
                    self.trades.append({
                        'entry_time': df.index[entry_idx],
                        'exit_time': df.index[i],
                        'type': 'BUY',
                        'entry_price': entry_price,
                        'exit_price': take_profit,
                        'pnl': pnl,
                        'pnl_pct': (pnl / (entry_price * position_size)) * 100,
                        'outcome': 'WIN'
                    })
                    position = None
                    
                elif position == 'SELL' and current_price <= take_profit:
                    pnl = (entry_price - take_profit) * position_size
                    balance += pnl
                    self.trades.append({
                        'entry_time': df.index[entry_idx],
                        'exit_time': df.index[i],
                        'type': 'SELL',
                        'entry_price': entry_price,
                        'exit_price': take_profit,
                        'pnl': pnl,
                        'pnl_pct': (pnl / (entry_price * position_size)) * 100,
                        'outcome': 'WIN'
                    })
                    position = None
            
            # Open new position
            if position is None and signals[i] != -1:
                entry_idx = i
                entry_price = current_price
                
                if signals[i] == 1:  # BUY
                    stop_loss = entry_price - (current_atr * self.atr_multiplier)
                    take_profit = entry_price + (current_atr * self.atr_multiplier * 2)
                    position = 'BUY'
                    position_size = self.calculate_position_size(balance, entry_price, stop_loss)
                    
                elif signals[i] == 0:  # SELL
                    stop_loss = entry_price + (current_atr * self.atr_multiplier)
                    take_profit = entry_price - (current_atr * self.atr_multiplier * 2)
                    position = 'SELL'
                    position_size = self.calculate_position_size(balance, entry_price, stop_loss)
            
            # Track equity
            self.equity_curve.append({
                'time': df.index[i],
                'balance': balance
            })
        
        # Calculate metrics
        results = self.calculate_metrics()
        self.print_results(results)
        
        return results
    
    def calculate_metrics(self):
        """
        Calculate performance metrics
        
        Returns:
            dict: Performance metrics
        """
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
            }
        
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['outcome'] == 'WIN'])
        losing_trades = len(trades_df[trades_df['outcome'] == 'LOSS'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # PnL metrics
        total_pnl = trades_df['pnl'].sum()
        total_return = ((self.initial_balance + total_pnl) / self.initial_balance - 1) * 100
        
        wins = trades_df[trades_df['outcome'] == 'WIN']['pnl']
        losses = trades_df[trades_df['outcome'] == 'LOSS']['pnl']
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        
        # Profit factor
        gross_profit = wins.sum() if len(wins) > 0 else 0
        gross_loss = abs(losses.sum()) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0
        
        # Drawdown
        equity_df['peak'] = equity_df['balance'].cummax()
        equity_df['drawdown'] = (equity_df['balance'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        # Sharpe ratio (simplified)
        returns = trades_df['pnl_pct']
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_balance': self.initial_balance + total_pnl,
        }
    
    def print_results(self, results):
        """
        Print backtest results
        """
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*60}")
        print(f"\n💰 ACCOUNT METRICS")
        print(f"   Initial Balance:  ${self.initial_balance:,.2f}")
        print(f"   Final Balance:    ${results['final_balance']:,.2f}")
        print(f"   Total P&L:        ${results['total_pnl']:,.2f}")
        print(f"   Total Return:     {results['total_return']:.2f}%")
        
        print(f"\n📊 TRADE STATISTICS")
        print(f"   Total Trades:     {results['total_trades']}")
        print(f"   Winning Trades:   {results['winning_trades']}")
        print(f"   Losing Trades:    {results['losing_trades']}")
        print(f"   Win Rate:         {results['win_rate']:.2f}%")
        
        print(f"\n💵 P&L METRICS")
        print(f"   Average Win:      ${results['avg_win']:,.2f}")
        print(f"   Average Loss:     ${results['avg_loss']:,.2f}")
        print(f"   Profit Factor:    {results['profit_factor']:.2f}")
        
        print(f"\n📉 RISK METRICS")
        print(f"   Max Drawdown:     {results['max_drawdown']:.2f}%")
        print(f"   Sharpe Ratio:     {results['sharpe_ratio']:.2f}")
        
        # Performance rating
        print(f"\n⭐ PERFORMANCE RATING")
        if results['total_return'] > 20 and results['win_rate'] > 60:
            print(f"   🏆 EXCELLENT - Strong returns with high win rate")
        elif results['total_return'] > 10 and results['win_rate'] > 50:
            print(f"   ✅ GOOD - Positive returns with decent win rate")
        elif results['total_return'] > 0:
            print(f"   ⚠️  MODERATE - Profitable but needs improvement")
        else:
            print(f"   ❌ POOR - Negative returns, review strategy")
    
    def plot_equity_curve(self, save_path=None):
        """
        Plot equity curve
        
        Args:
            save_path (str): Path to save plot (optional)
        """
        if len(self.equity_curve) == 0:
            print("⚠️  No equity data to plot")
            return
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        plt.figure(figsize=(12, 6))
        plt.plot(equity_df['time'], equity_df['balance'], linewidth=2, color='#2E86AB')
        plt.axhline(y=self.initial_balance, color='gray', linestyle='--', label='Initial Balance')
        plt.fill_between(equity_df['time'], self.initial_balance, equity_df['balance'], 
                         where=(equity_df['balance'] >= self.initial_balance), 
                         alpha=0.3, color='green', label='Profit')
        plt.fill_between(equity_df['time'], self.initial_balance, equity_df['balance'], 
                         where=(equity_df['balance'] < self.initial_balance), 
                         alpha=0.3, color='red', label='Loss')
        
        plt.title('Equity Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Balance ($)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"✅ Equity curve saved to: {save_path}")
        else:
            plt.show()
    
    def export_trades(self, filepath):
        """
        Export trades to CSV
        
        Args:
            filepath (str): Output file path
        """
        if len(self.trades) == 0:
            print("⚠️  No trades to export")
            return
        
        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filepath, index=False)
        print(f"✅ Trades exported to: {filepath}")


def load_model(model_path):
    """
    Load a saved model
    
    Args:
        model_path (str): Path to saved model
        
    Returns:
        dict: Model components
    """
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f"✅ Model loaded from: {model_path}")
    return model_data


def walk_forward_analysis(pipeline, df, window_size=5000, step_size=1000):
    """
    Perform walk-forward analysis
    
    Args:
        pipeline: GoldTradingMLPipeline instance
        df: Full dataset
        window_size: Size of training window
        step_size: Step size for sliding window
        
    Returns:
        list: Results for each window
    """
    print("\n" + "="*60)
    print("🚶 WALK-FORWARD ANALYSIS")
    print("="*60)
    
    results = []
    
    for i in range(0, len(df) - window_size, step_size):
        print(f"\nWindow {len(results)+1}: Rows {i} to {i+window_size}")
        
        train_data = df.iloc[i:i+window_size]
        test_data = df.iloc[i+window_size:i+window_size+step_size]
        
        # Prepare features
        X_train, y_train = pipeline.prepare_features_and_target(train_data)
        X_test, y_test = pipeline.prepare_features_and_target(test_data)
        
        # Scale
        X_train_scaled = pipeline.scaler.fit_transform(X_train)
        X_test_scaled = pipeline.scaler.transform(X_test)
        
        # Train
        pipeline.train_model(X_train_scaled, y_train)
        
        # Evaluate
        metrics = pipeline.evaluate_model(X_test_scaled, y_test)
        results.append(metrics)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"WALK-FORWARD SUMMARY")
    print(f"{'='*60}")
    
    avg_precision = np.mean([r['precision_smart'] for r in results])
    avg_f1 = np.mean([r['f1_smart'] for r in results])
    
    print(f"Average Precision: {avg_precision:.4f}")
    print(f"Average F1-Score:  {avg_f1:.4f}")
    
    return results


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   📊 BACKTESTING & EVALUATION UTILITIES 📊                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    This module provides backtesting and evaluation tools.
    
    Example usage:
    
    from evaluation_utils import TradingBacktest
    
    # Initialize backtester
    backtester = TradingBacktest(
        initial_balance=10000,
        risk_per_trade=0.02,
        atr_multiplier=2.0
    )
    
    # Run backtest
    results = backtester.run_backtest(df, signals, prices, atr_values)
    
    # Plot equity curve
    backtester.plot_equity_curve(save_path='equity_curve.png')
    
    # Export trades
    backtester.export_trades('trades.csv')
    """)


class BacktestEngine:
    """
    Simplified backtesting engine for signal-based strategies
    """
    
    def __init__(self, initial_capital=10000, position_size=0.1, commission=0.0003):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            position_size: Position size as fraction of capital
            commission: Commission per trade (as fraction)
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.commission = commission
        
    def run_backtest(self, signals_df):
        """
        Run backtest on signals
        
        Args:
            signals_df: DataFrame with columns ['time', 'price', 'signal', 'confidence']
            
        Returns:
            dict: Backtest results
        """
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(len(signals_df)):
            row = signals_df.iloc[i]
            price = row['price']
            signal = row['signal']
            
            # Close existing position and open new one
            if position != 0:
                # Close position
                if position > 0:  # Long position
                    pnl = (price - entry_price) * position - (position * price * self.commission)
                else:  # Short position
                    pnl = (entry_price - price) * abs(position) - (abs(position) * price * self.commission)
                
                capital += pnl
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'position_type': 'LONG' if position > 0 else 'SHORT'
                })
                position = 0
            
            # Open new position
            if signal == 'BUY':
                position = (capital * self.position_size) / price
                entry_price = price
            elif signal == 'SELL':
                position = -(capital * self.position_size) / price
                entry_price = price
            
            equity_curve.append(capital)
        
        # Calculate metrics
        trades_df = pd.DataFrame(trades)
        
        if len(trades_df) > 0:
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] <= 0])
            win_rate = (winning_trades / len(trades_df)) * 100
            total_profit = trades_df['pnl'].sum()
            
            # Sharpe ratio
            returns = pd.Series(equity_curve).pct_change().dropna()
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            
            # Max drawdown
            equity_series = pd.Series(equity_curve)
            rolling_max = equity_series.expanding().max()
            drawdowns = (equity_series - rolling_max) / rolling_max
            max_drawdown = abs(drawdowns.min()) * 100
            
            # Profit factor
            gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(trades_df[trades_df['pnl'] <= 0]['pnl'].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        else:
            winning_trades = 0
            losing_trades = 0
            win_rate = 0
            total_profit = 0
            sharpe = 0
            max_drawdown = 0
            profit_factor = 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': capital,
            'total_return': ((capital - self.initial_capital) / self.initial_capital) * 100,
            'total_profit': total_profit,
            'total_trades': len(trades_df),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'equity_curve': equity_curve,
            'trades_df': trades_df
        }


class ModelEvaluator:
    """
    Model evaluation utilities
    """
    
    @staticmethod
    def evaluate_model(y_true, y_pred, y_proba=None):
        """
        Evaluate model performance
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (optional)
            
        Returns:
            dict: Evaluation metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='binary', zero_division=0)
        }
        
        if y_proba is not None:
            from sklearn.metrics import roc_auc_score
            try:
                metrics['auc'] = roc_auc_score(y_true, y_proba)
            except:
                metrics['auc'] = 0.0
        
        return metrics
    
    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, save_path=None):
        """
        Plot confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path: Path to save plot (optional)
        """
        from sklearn.metrics import confusion_matrix
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
