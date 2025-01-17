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
        self._position_history = [
            {
                'entryTime': None,
                'closeTime': None,
                'side': None,
                'amount': None,
                'entryPrice': None,
                'closePrice': None,
                'return': None,
                'balance': self.INITIAL_BALANCE,
            }
        ]
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
        transaction_fee = self._symbol_info['taker']
        self._balance -= sign * notional * (1 + transaction_fee)
        current_time = self._historical_data.index[self._time_index + 1]
        if self._position.is_none():
            self._position.update(side, amount, price, current_time)
        else:
            entry_price = self._position.entry_price
            self._position_history.append(
                {
                    'entryTime': self._position.entry_time,
                    'closeTime': current_time,
                    'side': self._position.side,
                    'amount': amount,
                    'entryPrice': entry_price,
                    'closePrice': price,
                    'return': -sign * (price - entry_price) / entry_price,
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
        margin_asset = self._symbol_info['settle']
        return {'total': {margin_asset: self._balance}}

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
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
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
        trade_count = len(df) - 1
        if trade_count == 0:
            return {}
        df.loc[0, 'closeTime'] = df.loc[1, 'entryTime']
        self._export_to_excel(df, '../simulation-history.xlsx')

        win_count = (df['return'] > 0.0).sum()
        lose_count = (df['return'] < 0.0).sum()
        win_rate = win_count / trade_count

        pnl = df['balance'].diff().iloc[1:]
        avg_profit = pnl[pnl > 0.0].sum() / win_count if win_count > 0 else 0
        avg_loss = pnl[pnl < 0.0].sum() / lose_count if lose_count > 0 else 0
        pnl_ratio = avg_profit / -avg_loss if avg_loss < 0 else inf

        max_profit_rate = df['return'].max()
        max_loss_rate = df['return'].min()
        final_balance = df['balance'].iloc[-1]

        return {
            'Number of trades': f'{trade_count}',
            'Win rate': f'{win_rate:.1%}',
            'P&L ratio': f'{pnl_ratio:.2f}',
            'Max profit rate (per trade)': f'{max_profit_rate:.1%}',
            'Max loss rate (per trade)': f'{max_loss_rate:.1%}',
            'Final balance': f'{final_balance:.1f}',
        }

    def _export_to_excel(self, df: pd.DataFrame, filename: str) -> None:
        """Export the DataFrame to Excel.

        Save the DataFrame to an Excel file and chart the change in
        balance over transactions.

        Args:
            df: The DataFrame containing the position history.
            filename: The path to save the Excel file.
        """

        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Position')
            wb = writer.book
            ws = writer.sheets['Position']

            precision = self._symbol_info['precision']
            amount_precision = str(precision['amount']).replace('1', '0')
            price_precision = str(precision['price']).replace('1', '0')

            amount_format = wb.add_format({'num_format': amount_precision})
            price_format = wb.add_format({'num_format': price_precision})
            return_format = wb.add_format({'num_format': '0.0%'})
            balance_format = wb.add_format({'num_format': '0.0'})

            ws.set_column('B:C', width=18.63)
            ws.set_column('E:E', width=7.00, cell_format=amount_format)
            ws.set_column('F:G', width=8.75, cell_format=price_format)
            ws.set_column('H:H', width=7.00, cell_format=return_format)
            ws.set_column('I:I', width=9.25, cell_format=balance_format)

            margin_asset = self._symbol_info['settle']
            chart = wb.add_chart({'type': 'line'})
            chart.set_legend({'none': True})
            chart.set_title({'name': f'{margin_asset} balance'})
            chart.set_x_axis({'num_format': 'mm-dd'})

            first_row, last_row = 1, len(df) + 1
            closed_col = df.columns.get_loc('closeTime') + 1
            balance_col = df.columns.get_loc('balance') + 1
            chart.add_series(
                {
                    'categories': [
                        ws.name,
                        first_row,
                        closed_col,
                        last_row,
                        closed_col,
                    ],
                    'values': [
                        ws.name,
                        first_row,
                        balance_col,
                        last_row,
                        balance_col,
                    ],
                }
            )
            ws.insert_chart('K3', chart)
