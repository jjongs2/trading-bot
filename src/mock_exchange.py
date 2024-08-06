"""Define a MockExchange class that simulates a crypto exchange."""

from math import inf

import ccxt
import pandas as pd

from config import Config
from position import Position
from side import Side

OHLCV_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

config = Config()
exchange_class = getattr(ccxt, config.EXCHANGE_ID)


class MockExchange(exchange_class):
    """Simulate a crypto exchange for backtesting.

    Inherit from the real exchange class and override key methods of the
    real exchange to provide simulated behavior. Maintain internal
    states for realistic simulation of trading scenarios.

    Attributes:
        INITIAL_BALANCE: The initial balance for the simulated account.
    """

    INITIAL_BALANCE = 1000

    def __init__(self, *args, **kwargs):
        """Initialize the instance with default values."""
        super().__init__(*args, **kwargs)
        self._balance = self.INITIAL_BALANCE
        self._historical_data = None
        self._position = Position()
        self._position_history = []
        self._symbol_info = None
        self._time_index = -1

    def cancel_all_orders(self, *args, **kwargs) -> list:
        """Do nothing."""
        pass

    def create_order(
        self,
        side: Side,
        amount: float,
        price: float,
        *args,
        **kwargs,
    ) -> dict:
        """Simulate creating an order and update internal states.

        Args:
            side: The side of the order.
            amount: The amount of the base asset to trade.
            price: The price to trade at.

        Returns:
            A dict containing the details of the simulated order.
        """
        sign = side.sign()
        notional = amount * price
        self._balance -= sign * notional * (1 + self._symbol_info['taker'])
        current_time = self._historical_data.index[self._time_index + 1]
        if self._position.is_none():
            self._position.update(side, amount, price, current_time)
        else:
            entry_price = self._position.entry_price
            self._position_history.append(
                {
                    'opened': self._position.entry_time,
                    'closed': current_time,
                    'side': self._position.side,
                    'amount': amount,
                    'entryPrice': entry_price,
                    'closePrice': price,
                    'returnRate': -sign * (price - entry_price) / entry_price,
                    'balance': self._balance,
                }
            )
            self._position.close()
        return {
            'time': current_time,
            'side': side,
            'amount': amount,
            'price': price,
        }

    def fetch_balance(self, *args, **kwargs) -> dict:
        """Simulate fetching an account balance.

        Returns:
            A dict containing the simulated account balance.
        """
        return {'total': {self._symbol_info['settle']: self._balance}}

    def fetch_ohlcv(self, *args, **kwargs) -> list:
        """Fetch OHLCV data.

        Update internal historical data and return actual OHLCV data.

        Returns:
            A list of lists containing the actual OHLCV data.
        """
        data = super().fetch_ohlcv(*args, **kwargs)
        if not data:
            return data
        df = pd.DataFrame(data=data, columns=OHLCV_COLUMNS)
        df['timestamp'] = pd.to_datetime(
            arg=df['timestamp'],
            utc=True,
            unit='ms',
        ).astype(str)
        df.set_index('timestamp', inplace=True)
        if self._historical_data is None:
            self._historical_data = df.iloc[config.WINDOW_SIZE - 1 :]
        else:
            self._historical_data = pd.concat([self._historical_data, df])
        return data

    def fetch_positions(self, *args, **kwargs) -> list:
        """Simulate fetching the current position.

        Returns:
            A list containing the current position, or an empty list if
            there's no position.
        """
        if self._position.is_none():
            return []
        return [
            {
                'contracts': self._position.amount,
                'entryPrice': self._position.entry_price,
                'side': self._position.side,
            },
        ]

    def load_markets(self, *args, **kwargs) -> dict:
        """Load actual market data and set internal parameters.

        Returns:
            A dict containing actual market data.
        """
        markets = super().load_markets(*args, **kwargs)
        self._symbol_info = markets[config.SYMBOL]
        return markets

    def next(self) -> int | None:
        """Advance the simulation to the next time step.

        Returns:
            New time index, or None if the end of the data is reached.
        """
        self._time_index += 1
        if self._time_index >= len(self._historical_data) - 1:
            return None
        return self._time_index

    def pnl_analysis(self) -> dict:
        """Perform a PNL analysis on the simulated transaction history.

        Returns:
            A dict containing various metrics.
        """
        df = pd.DataFrame(self._position_history)
        df.to_excel('../simulation-result.xlsx')
        trade_count = len(df)
        if trade_count == 0:
            return {}

        win_count = (df['returnRate'] > 0.0).sum()
        lose_count = (df['returnRate'] < 0.0).sum()
        win_rate = win_count / trade_count

        pnl = df['balance'].diff()
        pnl.iloc[0] = df['balance'].iloc[0] - self.INITIAL_BALANCE
        avg_profit = pnl[pnl > 0.0].sum() / win_count if win_count > 0 else 0
        avg_loss = pnl[pnl < 0.0].sum() / lose_count if lose_count > 0 else 0
        pnl_ratio = avg_profit / -avg_loss if avg_loss < 0 else inf

        max_profit_rate = df['returnRate'].max()
        max_loss_rate = df['returnRate'].min()

        return {
            'Number of trades': f'{trade_count}',
            'Win rate': f'{win_rate:.1%}',
            'P&L ratio': f'{pnl_ratio:.2f}',
            'Max profit rate (per trade)': f'{max_profit_rate:.1%}',
            'Max loss rate (per trade)': f'{max_loss_rate:.1%}',
            'Final balance': f"{df['balance'].iloc[-1]:.1f}",
        }
