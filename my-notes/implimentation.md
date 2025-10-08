# Indian Options Trading System - Implementation Guide

## Project Overview
Building an institutional-grade options trading system for Indian markets using OpenAlgo for data/execution, with focus on strategy and risk management layers.

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA & EXECUTION LAYER                    │
│                  (OpenAlgo - Already Handled)                │
│  • Broker Integration (Zerodha/Angel/Fyers/Shoonya)        │
│  • Real-time Market Data (NSE Options Chain)                │
│  • Order Placement & Management                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    STRATEGY LAYER                            │
│  • Options Strategy Engine (QuantConnect LEAN adapted)      │
│  • Strategy Library (Iron Condor, Straddle, etc.)          │
│  • Greeks Calculator (py_vollib)                            │
│  • Signal Generator                                         │
│  • Backtesting Engine (VectorBT)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 RISK MANAGEMENT LAYER                        │
│  • Portfolio Greeks Aggregation (Riskfolio-Lib)            │
│  • Position Sizing & Limits                                 │
│  • Stop Loss / Take Profit Management                       │
│  • Margin Monitoring (SPAN + Exposure)                      │
│  • Drawdown Control                                         │
│  • Performance Analytics (QuantStats)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
indian-options-trading-system/
│
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Global configuration
│   ├── broker_config.py             # OpenAlgo broker settings
│   └── strategy_config.py           # Strategy parameters
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── openalgo_client.py      # OpenAlgo API wrapper
│   │   ├── options_chain.py        # Options chain data handler
│   │   └── data_store.py           # Time-series data storage
│   │
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py        # Abstract base strategy class
│   │   ├── iron_condor.py          # Iron Condor implementation
│   │   ├── straddle.py             # Long/Short Straddle
│   │   ├── strangle.py             # Long/Short Strangle
│   │   ├── butterfly.py            # Butterfly Spread
│   │   ├── calendar_spread.py      # Calendar Spread
│   │   ├── delta_neutral.py        # Delta-neutral strategy
│   │   └── strategy_manager.py     # Strategy orchestration
│   │
│   ├── greeks/
│   │   ├── __init__.py
│   │   ├── calculator.py           # Greeks calculation (py_vollib)
│   │   ├── portfolio_greeks.py     # Aggregate portfolio Greeks
│   │   └── iv_surface.py           # Implied Volatility surface
│   │
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── position_sizer.py       # Kelly Criterion, Fixed %
│   │   ├── portfolio_optimizer.py  # Riskfolio-Lib integration
│   │   ├── risk_limits.py          # Greeks-based limits
│   │   ├── stop_loss.py            # SL/TP management
│   │   ├── margin_monitor.py       # SPAN margin monitoring
│   │   └── var_calculator.py       # Value at Risk
│   │
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── vectorbt_engine.py      # VectorBT backtesting
│   │   ├── performance_metrics.py  # QuantStats integration
│   │   └── backtest_runner.py      # Backtest orchestration
│   │
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── order_manager.py        # Order execution via OpenAlgo
│   │   ├── position_tracker.py     # Track open positions
│   │   └── trade_logger.py         # Log all trades
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging setup
│       ├── helpers.py              # Utility functions
│       └── validators.py           # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── test_strategies/
│   ├── test_risk/
│   └── test_greeks/
│
├── notebooks/
│   ├── 01_strategy_analysis.ipynb
│   ├── 02_backtest_results.ipynb
│   └── 03_risk_analysis.ipynb
│
├── scripts/
│   ├── run_backtest.py             # Run historical backtest
│   ├── run_live_trading.py         # Live trading bot
│   ├── run_paper_trading.py        # Paper trading simulation
│   └── generate_report.py          # Generate performance report
│
├── data/                           # Local data storage
│   ├── historical/
│   ├── backtests/
│   └── logs/
│
└── docs/
    ├── STRATEGY_GUIDE.md
    ├── RISK_MANAGEMENT.md
    └── API_REFERENCE.md
```

---

## 🔧 Phase 1: Environment Setup

### Step 1.1: Create `requirements.txt`

```txt
# Core Dependencies
python>=3.10

# OpenAlgo Integration
requests>=2.31.0
websocket-client>=1.6.0

# Data Processing
pandas>=2.1.0
numpy>=1.24.0
polars>=0.19.0

# Options Analytics
py-vollib>=1.0.1
mibian>=0.1.3
scipy>=1.11.0

# Strategy & Backtesting
vectorbt>=0.26.0
bt>=1.0.0

# Risk Management
riskfolio-lib>=5.0.0
pypfopt>=1.5.5
quantstats>=0.0.62

# Technical Analysis
ta-lib>=0.4.28
pandas-ta>=0.3.14

# Machine Learning (Optional)
scikit-learn>=1.3.0
xgboost>=2.0.0

# Database
redis>=5.0.0
sqlalchemy>=2.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
loguru>=0.7.0
pyyaml>=6.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# API Framework
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Step 1.2: Create `.env.example`

```bash
# OpenAlgo Configuration
OPENALGO_API_KEY=your_api_key_here
OPENALGO_HOST=http://127.0.0.1:5000
BROKER_NAME=zerodha  # zerodha, angel, fyers, shoonya

# Trading Parameters
TRADING_MODE=paper  # paper, live
SYMBOL=NIFTY
EXCHANGE=NFO
TIMEZONE=Asia/Kolkata

# Risk Management
MAX_PORTFOLIO_DELTA=100
MAX_PORTFOLIO_GAMMA=50
MAX_PORTFOLIO_VEGA=500
MAX_POSITION_SIZE_PCT=5.0
MAX_DRAWDOWN_PCT=10.0
MAX_LOSS_PER_TRADE=2000

# Strategy Settings
DEFAULT_STRATEGY=iron_condor
ENABLE_STOP_LOSS=true
ENABLE_TAKE_PROFIT=true
STOP_LOSS_PCT=50
TAKE_PROFIT_PCT=50

# Database
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=sqlite:///data/trading.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/trading.log
```

---

## 🔧 Phase 2: Core Configuration

### Step 2.1: Create `config/settings.py`

```python
"""
Global configuration settings
"""
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = DATA_DIR / "logs"
    
    # OpenAlgo
    OPENALGO_API_KEY: str
    OPENALGO_HOST: str = "http://127.0.0.1:5000"
    BROKER_NAME: str = "zerodha"
    
    # Trading
    TRADING_MODE: Literal["paper", "live"] = "paper"
    SYMBOL: str = "NIFTY"
    EXCHANGE: str = "NFO"
    TIMEZONE: str = "Asia/Kolkata"
    
    # Risk Limits
    MAX_PORTFOLIO_DELTA: float = 100.0
    MAX_PORTFOLIO_GAMMA: float = 50.0
    MAX_PORTFOLIO_VEGA: float = 500.0
    MAX_POSITION_SIZE_PCT: float = 5.0
    MAX_DRAWDOWN_PCT: float = 10.0
    MAX_LOSS_PER_TRADE: float = 2000.0
    
    # Strategy
    DEFAULT_STRATEGY: str = "iron_condor"
    ENABLE_STOP_LOSS: bool = True
    ENABLE_TAKE_PROFIT: bool = True
    STOP_LOSS_PCT: float = 50.0
    TAKE_PROFIT_PCT: float = 50.0
    
    # Database
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DATABASE_URL: str = "sqlite:///data/trading.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/trading.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
```

### Step 2.2: Create `config/strategy_config.py`

```python
"""
Strategy-specific configurations
"""
from typing import Dict, Any
from enum import Enum


class StrategyType(Enum):
    """Available strategy types"""
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    CALENDAR_SPREAD = "calendar_spread"
    DELTA_NEUTRAL = "delta_neutral"


# Strategy Parameters
STRATEGY_PARAMS: Dict[str, Dict[str, Any]] = {
    "iron_condor": {
        "call_width": 200,  # Points between call strikes
        "put_width": 200,   # Points between put strikes
        "target_delta": 0.30,  # Delta for short strikes
        "dte_entry": 7,     # Days to expiry for entry
        "dte_exit": 2,      # Days to expiry for exit
        "profit_target": 0.50,  # 50% of max profit
        "stop_loss": 2.0,   # 2x max profit
        "max_positions": 3,
    },
    
    "straddle": {
        "direction": "long",  # long or short
        "atm_offset": 0,      # Offset from ATM
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.30,
        "stop_loss": 0.50,
        "iv_percentile_min": 30,  # Enter when IV > 30th percentile
    },
    
    "strangle": {
        "direction": "long",
        "call_delta": 0.30,
        "put_delta": 0.30,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.40,
        "stop_loss": 0.60,
        "iv_percentile_min": 40,
    },
    
    "butterfly": {
        "wing_width": 100,  # Points between strikes
        "atm_offset": 0,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.50,
        "stop_loss": 1.0,
    },
    
    "calendar_spread": {
        "strike_selection": "atm",  # atm, otm, itm
        "front_month_dte": 7,
        "back_month_dte": 30,
        "profit_target": 0.30,
        "stop_loss": 0.50,
    },
    
    "delta_neutral": {
        "delta_threshold": 5,  # Rebalance if delta > this
        "rebalance_frequency": "daily",
        "target_allocation": {
            "calls": 0.5,
            "puts": 0.5,
        },
    },
}


# Indian Market Specific
MARKET_HOURS = {
    "pre_market_start": "09:00",
    "market_open": "09:15",
    "market_close": "15:30",
    "post_market_end": "16:00",
}

# Weekly Expiry Days
WEEKLY_EXPIRY = {
    "NIFTY": "Thursday",
    "BANKNIFTY": "Wednesday",
    "FINNIFTY": "Tuesday",
    "MIDCPNIFTY": "Monday",
}

# Contract Specifications
CONTRACT_SPECS = {
    "NIFTY": {
        "lot_size": 50,
        "tick_size": 0.05,
        "strike_gap": 50,
    },
    "BANKNIFTY": {
        "lot_size": 15,
        "tick_size": 0.05,
        "strike_gap": 100,
    },
    "FINNIFTY": {
        "lot_size": 40,
        "tick_size": 0.05,
        "strike_gap": 50,
    },
}
```

---

## 🔧 Phase 3: Data Layer (OpenAlgo Integration)

### Step 3.1: Create `src/data/openalgo_client.py`

```python
"""
OpenAlgo API Client Wrapper
"""
import requests
from typing import Dict, List, Optional, Any
from loguru import logger
from config.settings import settings


class OpenAlgoClient:
    """
    Wrapper for OpenAlgo API
    Docs: https://docs.openalgo.in/trading-platform/python
    """
    
    def __init__(self):
        self.host = settings.OPENALGO_HOST
        self.api_key = settings.OPENALGO_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.host}/api/v1/{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # Market Data Methods
    def get_quotes(self, symbol: str, exchange: str = "NFO") -> Dict:
        """Get real-time quotes"""
        return self._request("POST", "quotes", {
            "symbol": symbol,
            "exchange": exchange
        })
    
    def get_option_chain(self, symbol: str, expiry: str) -> List[Dict]:
        """Get options chain data"""
        return self._request("POST", "optionchain", {
            "symbol": symbol,
            "expiry": expiry
        })
    
    def get_depth(self, symbol: str, exchange: str = "NFO") -> Dict:
        """Get market depth"""
        return self._request("POST", "depth", {
            "symbol": symbol,
            "exchange": exchange
        })
    
    # Order Management Methods
    def place_order(
        self,
        symbol: str,
        exchange: str,
        action: str,  # BUY or SELL
        quantity: int,
        price: float,
        product: str = "MIS",
        order_type: str = "LIMIT",
        **kwargs
    ) -> Dict:
        """Place an order"""
        order_data = {
            "symbol": symbol,
            "exchange": exchange,
            "action": action,
            "quantity": quantity,
            "price": price,
            "product": product,
            "order_type": order_type,
            **kwargs
        }
        return self._request("POST", "placeorder", order_data)
    
    def modify_order(self, order_id: str, quantity: Optional[int] = None, 
                     price: Optional[float] = None) -> Dict:
        """Modify existing order"""
        data = {"order_id": order_id}
        if quantity:
            data["quantity"] = quantity
        if price:
            data["price"] = price
        return self._request("POST", "modifyorder", data)
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        return self._request("POST", "cancelorder", {"order_id": order_id})
    
    def get_order_book(self) -> List[Dict]:
        """Get all orders"""
        return self._request("GET", "orderbook")
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        return self._request("GET", "positions")
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings"""
        return self._request("GET", "holdings")
    
    def close_position(self, symbol: str, exchange: str, product: str = "MIS") -> Dict:
        """Close a position"""
        return self._request("POST", "closeposition", {
            "symbol": symbol,
            "exchange": exchange,
            "product": product
        })
    
    # Account Methods
    def get_funds(self) -> Dict:
        """Get account funds"""
        return self._request("GET", "funds")
    
    def get_margins(self, positions: List[Dict]) -> Dict:
        """Calculate margin requirements"""
        return self._request("POST", "margins", {"positions": positions})


# Global client instance
openalgo = OpenAlgoClient()
```

### Step 3.2: Create `src/data/options_chain.py`

```python
"""
Options chain data handler
"""
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
from src.data.openalgo_client import openalgo
from config.strategy_config import CONTRACT_SPECS


class OptionsChainHandler:
    """Handle options chain data"""
    
    def __init__(self, symbol: str = "NIFTY"):
        self.symbol = symbol
        self.contract_spec = CONTRACT_SPECS.get(symbol, {})
        
    def get_expiry_dates(self, num_expiries: int = 4) -> List[str]:
        """Get next N expiry dates"""
        # This would use OpenAlgo API or calculate based on weekly expiry
        # For now, simplified version
        today = datetime.now()
        expiries = []
        for i in range(num_expiries):
            expiry = today + timedelta(weeks=i)
            expiries.append(expiry.strftime("%Y-%m-%d"))
        return expiries
    
    def get_chain(self, expiry: Optional[str] = None) -> pd.DataFrame:
        """
        Get options chain as DataFrame
        
        Returns:
            DataFrame with columns: strike, call_ltp, put_ltp, call_iv, put_iv, etc.
        """
        if not expiry:
            expiries = self.get_expiry_dates()
            expiry = expiries[0]  # Use nearest expiry
        
        try:
            chain_data = openalgo.get_option_chain(self.symbol, expiry)
            df = pd.DataFrame(chain_data)
            
            # Process and clean data
            df = self._process_chain_data(df)
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch options chain: {e}")
            return pd.DataFrame()
    
    def _process_chain_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw chain data"""
        # Add calculated fields
        df['call_oi_change'] = df.get('call_oi', 0) - df.get('call_oi_prev', 0)
        df['put_oi_change'] = df.get('put_oi', 0) - df.get('put_oi_prev', 0)
        df['pcr'] = df.get('put_oi', 0) / df.get('call_oi', 1)
        
        # Sort by strike
        df = df.sort_values('strike')
        return df
    
    def get_atm_strike(self, spot_price: Optional[float] = None) -> float:
        """Get ATM strike price"""
        if not spot_price:
            quotes = openalgo.get_quotes(self.symbol, "NSE")
            spot_price = quotes.get('ltp', 0)
        
        strike_gap = self.contract_spec.get('strike_gap', 50)
        atm = round(spot_price / strike_gap) * strike_gap
        return atm
    
    def get_strikes_by_delta(
        self, 
        target_delta: float, 
        option_type: str = "CE",
        expiry: Optional[str] = None
    ) -> List[float]:
        """Find strikes closest to target delta"""
        chain = self.get_chain(expiry)
        
        if option_type == "CE":
            delta_col = "call_delta"
        else:
            delta_col = "put_delta"
        
        if delta_col not in chain.columns:
            logger.warning(f"Delta column {delta_col} not found")
            return []
        
        chain['delta_diff'] = abs(chain[delta_col] - target_delta)
        closest_strikes = chain.nsmallest(3, 'delta_diff')['strike'].tolist()
        
        return closest_strikes
    
    def get_iv_percentile(self, window_days: int = 30) -> float:
        """Calculate IV percentile (requires historical data)"""
        # This would need historical IV data
        # Placeholder implementation
        return 50.0
    
    def get_option_greeks(self, strike: float, option_type: str, expiry: str) -> Dict:
        """Get Greeks for specific option"""
        chain = self.get_chain(expiry)
        row = chain[chain['strike'] == strike]
        
        if row.empty:
            return {}
        
        prefix = "call" if option_type == "CE" else "put"
        greeks = {
            'delta': row[f'{prefix}_delta'].values[0],
            'gamma': row[f'{prefix}_gamma'].values[0],
            'theta': row[f'{prefix}_theta'].values[0],
            'vega': row[f'{prefix}_vega'].values[0],
            'iv': row[f'{prefix}_iv'].values[0],
        }
        return greeks
```

---

## 🔧 Phase 4: Strategy Layer

### Step 4.1: Create `src/strategies/base_strategy.py`

```python
"""
Abstract base strategy class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


@dataclass
class Position:
    """Represents an options position"""
    symbol: str
    strike: float
    option_type: str  # CE or PE
    quantity: int
    entry_price: float
    current_price: float
    expiry: str
    order_id: Optional[str] = None
    
    @property
    def pnl(self) -> float:
        """Calculate P&L"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_pct(self) -> float:
        """Calculate P&L percentage"""
        if self.entry_price == 0:
            return 0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class Signal:
    """Trading signal"""
    action: str  # ENTER, EXIT, ADJUST
    legs: List[Dict[str, Any]]  # List of option legs
    reason: str
    timestamp: datetime
    metadata: Optional[Dict] = None


class BaseStrategy(ABC):
    """Abstract base class for all strategies"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name
        self.params = params
        self.positions: List[Position] = []
        self.signals: List[Signal] = []
        self.pnl = 0.0
        
    @abstractmethod
    def generate_signal(self, market_data: Dict) -> Optional[Signal]:
        """
        Generate trading signal based on market data
        
        Args:
            market_data: Dictionary containing options chain, spot price, etc.
            
        Returns:
            Signal object or None
        """
        pass
    
    @abstractmethod
    def should_exit(self, position: Position, market_data: Dict) -> bool:
        """
        Check if position should be exited
        
        Args:
            position: Current position
            market_data: Current market data
            
        Returns:
            Boolean indicating if position should be closed
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, available_capital: float) -> int:
        """
        Calculate position size (number of lots)
        
        Args:
            available_capital: Available trading capital
            
        Returns:
            Number of lots to trade
        """
        pass
    
    def update_positions(self, current_prices: Dict[str, float]):
        """Update current prices for all positions"""
        for position in self.positions:
            key = f"{position.symbol}_{position.strike}_{position.option_type}"
            if key in current_prices:
                position.current_price = current_prices[key]
    
    def get_total_pnl(self) -> float:
        """Calculate total P&L across all positions"""
        return sum(pos.pnl for pos in self.positions)
    
    def get_portfolio_greeks(self) -> Dict[str, float]:
        """Calculate aggregate portfolio Greeks"""
        # This will be implemented with Greeks calculator
        return {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
        }
    
    def add_position(self, position: Position):
        """Add a new position"""
        self.positions.append(position)
        logger.info(f"Added position: {position.symbol} {position.strike} {position.option_type}")
    
    def remove_position(self, position: Position):
        """Remove a position"""
        if position in self.positions:
            self.positions.remove(position)
            logger.info(f"Removed position: {position.symbol} {position.strike} {position.option_type}")
    
    def log_signal(self, signal: Signal):
        """Log a trading signal"""
        self.signals.append(signal)
        logger.info(f"Signal generated: {signal.action} - {signal.reason}")
    
    def get_strategy_state(self) -> Dict:
        """Get current strategy state"""
        return {
            'name': self.name,
            'positions': len(self.positions),
            'total_pnl': self.get_total_pnl(),
            'signals': len(self.signals),
        }
```

### Step 4.2: Create `src/strategies/iron_condor.py`

```python
"""
Iron Condor Strategy Implementation
"""
from typing import Dict, List, Optional
from datetime import datetime
from src.strategies.base_strategy import BaseStrategy, Signal, Position
from src.data.options_chain import OptionsChainHandler
from config.strategy_config import STRATEGY_PARAMS
from loguru import logger


class IronCondorStrategy(BaseStrategy):
    """
    Iron Condor: Neutral strategy selling OTM call and put spreads
    
    Structure:
    - Sell OTM Call
    - Buy further OTM Call (protection)
    - Sell OTM Put  
    - Buy further OTM Put (protection)
    
    Max Profit: Net premium received
    Max Loss: Width of spread - premium received
    """
    
    def __init__(self, symbol: str = "NIFTY"):
        params = STRATEGY_PARAMS["iron_condor"]
        super().__init__(name="IronCondor", params=params)
        
        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)
        
        # Extract parameters
        self.call_width = params["call_width"]
        self.put_width = params["put_width"]
        self.target_delta = params["target_delta"]
        self.dte_entry = params["dte_entry"]
        self.dte_exit = params["dte_exit"]
        self.profit_target = params["profit_target"]
        self.stop_loss = params["stop_loss"]
        self.max_positions = params["max_positions"]
        
    def generate_signal(self, market_data: Dict) -> Optional[Signal]:
        """
        Generate Iron Condor entry signal
        
        market_data should contain:
        - spot_price: Current underlying price
        - options_chain: Options chain DataFrame
        - dte: Days to expiry
        - iv_percentile: IV percentile (optional)
        """
        # Check if we're at max positions
        if len(self.positions) >= self.max_positions:
            return None
        
        spot_price = market_data.get('spot_price')
        dte = market_data.get('dte', 7)
        
        # Only enter if DTE matches our criteria
        if dte != self.dte_entry:
            return None
        
        # Find strikes
        atm_strike = self.chain_handler.get_atm_strike(spot_price)
        
        # Find call strikes by delta
        call_strikes = self.chain_handler.get_strikes_by_delta(
            self.target_delta, 
            option_type="CE"
        )
        
        # Find put strikes by delta  
        put_strikes = self.chain_handler.get_strikes_by_delta(
            self.target_delta,
            option_type="PE"
        )
        
        if not call_strikes or not put_strikes:
            logger.warning("Could not find suitable strikes")
            return None
        
        # Select strikes
        short_call_strike = call_strikes[0]
        long_call_strike = short_call_strike + self.call_width
        
        short_put_strike = put_strikes[0]
        long_put_strike = short_put_strike - self.put_width
        
        # Create legs
        legs = [
            {
                'action': 'SELL',
                'strike': short_call_strike,
                'option_type': 'CE',
                'quantity': 1,
            },
            {
                'action': 'BUY',
                'strike': long_call_strike,
                'option_type': 'CE',
                'quantity': 1,
            },
            {
                'action': 'SELL',
                'strike': short_put_strike,
                'option_type': 'PE',
                'quantity': 1,
            },
            {
                'action': 'BUY',
                'strike': long_put_strike,
                'option_type': 'PE',
                'quantity': 1,
            },
        ]
        
        signal = Signal(
            action='ENTER',
            legs=legs,
            reason=f"Iron Condor entry at DTE={dte}, ATM={atm_strike}",
            timestamp=datetime.now(),
            metadata={
                'atm_strike': atm_strike,
                'dte': dte,
                'max_profit': self._calculate_max_profit(legs, market_data),
                'max_loss': self._calculate_max_loss(legs),
            }
        )
        
        return signal
    
    def should_exit(self, position: Position, market_data: Dict) -> bool:
        """
        Check exit conditions:
        1. Profit target reached (50% of max profit)
        2. Stop loss hit (2x max profit)
        3. DTE threshold reached
        """
        dte = market_data.get('dte', 7)
        
        # Exit at DTE threshold
        if dte <= self.dte_exit:
            logger.info(f"Exiting due to DTE={dte}")
            return True
        
        # Get position P&L
        pnl = position.pnl
        max_profit = position.entry_price  # Simplified
        
        # Profit target
        if pnl >= (max_profit * self.profit_target):
            logger.info(f"Profit target reached: {pnl}")
            return True
        
        # Stop loss
        max_loss = max_profit * self.stop_loss
        if abs(pnl) >= max_loss:
            logger.info(f"Stop loss hit: {pnl}")
            return True
        
        return False
    
    def calculate_position_size(self, available_capital: float) -> int:
        """
        Calculate number of Iron Condors to trade
        Risk max 5% of capital per position
        """
        risk_per_position = available_capital * 0.05
        
        # Max loss per IC = width - premium
        max_loss_per_ic = max(self.call_width, self.put_width)
        
        num_lots = int(risk_per_position / max_loss_per_ic)
        return max(1, num_lots)
    
    def _calculate_max_profit(self, legs: List[Dict], market_data: Dict) -> float:
        """Calculate maximum profit for Iron Condor"""
        # Max profit = Net premium received
        # Simplified calculation - would need actual option prices
        return 0.0  # Placeholder
    
    def _calculate_max_loss(self, legs: List[Dict]) -> float:
        """Calculate maximum loss"""
        # Max loss = Width of widest spread - net premium
        return max(self.call_width, self.put_width)
    
    def adjust_position(self, position: Position, market_data: Dict) -> Optional[Signal]:
        """
        Adjust Iron Condor if tested
        - Roll untested side closer
        - Convert to Iron Fly
        - Close tested side
        """
        spot_price = market_data.get('spot_price')
        
        # Check if position is tested
        # (Spot moved through short strike)
        
        # Adjustment logic here
        # Return adjustment signal if needed
        
        return None
```

---

## 📝 Implementation Instructions for Claude Code

### Phase 1: Initial Setup (Priority 1)
```bash
# 1. Create project structure
# 2. Install dependencies from requirements.txt
# 3. Create .env file from .env.example
# 4. Verify OpenAlgo connection
```

### Phase 2: Core Components (Priority 2)
```bash
# 1. Implement config files (settings.py, strategy_config.py)
# 2. Implement OpenAlgo client wrapper
# 3. Implement options chain handler
# 4. Create base strategy class
# 5. Implement Iron Condor strategy
```

### Phase 3: Greeks & Risk (Priority 3)
```bash
# 1. Implement Greeks calculator using py_vollib
# 2. Implement portfolio Greeks aggregation
# 3. Implement risk limits checker
# 4. Implement position sizer
# 5. Implement stop loss manager
```

### Phase 4: Execution & Backtesting (Priority 4)
```bash
# 1. Implement order manager
# 2. Implement position tracker
# 3. Implement VectorBT backtesting engine
# 4. Implement performance metrics
# 5. Create backtest runner script
```

### Phase 5: Additional Strategies (Priority 5)
```bash
# 1. Implement Straddle strategy
# 2. Implement Strangle strategy
# 3. Implement Butterfly strategy
# 4. Implement Calendar Spread
# 5. Implement Delta Neutral strategy
```

### Phase 6: Testing & Documentation (Priority 6)
```bash
# 1. Write unit tests for all components
# 2. Write integration tests
# 3. Create documentation
# 4. Create example notebooks
# 5. Create deployment guide
```

---

## 🎯 Success Criteria

Each component should:
1. ✅ Have proper error handling
2. ✅ Include logging with loguru
3. ✅ Have type hints
4. ✅ Include docstrings
5. ✅ Be testable
6. ✅ Follow Indian market conventions

---

## 🚀 Next Steps for Implementation

**Start with Phase 2 - I've provided the complete structure and key files above.**

Would you like me to:
1. **Continue with Phase 3** (Greeks calculation & risk management)?
2. **Provide complete implementation** of remaining strategy files?
3. **Create the backtesting engine** with VectorBT?
4. **Build the execution layer** with order management?

Let me know which phase you want me to elaborate on next! 🎯