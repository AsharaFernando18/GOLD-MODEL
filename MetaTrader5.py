"""
Mock MetaTrader5 module for testing purposes
This allows the code to be tested in environments where MT5 is not available
"""

# Constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440

def initialize(*args, **kwargs):
    """Mock MT5 initialization"""
    print("⚠️  Using Mock MT5 - No real connection")
    return True

def shutdown():
    """Mock MT5 shutdown"""
    pass

def copy_rates_from_pos(symbol, timeframe, start, count):
    """Mock data fetch - returns None to trigger fallback"""
    return None

def last_error():
    """Mock error function"""
    return (0, "Mock MT5 - No real connection")

def terminal_info():
    """Mock terminal info"""
    class TerminalInfo:
        connected = False
    return TerminalInfo()

def account_info():
    """Mock account info"""
    return None

print("⚠️  MetaTrader5 mock module loaded (for testing only)")
