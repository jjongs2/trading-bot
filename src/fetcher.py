from logging import getLogger

import ccxt
import pandas as pd

from position import Position
from side import Side

OHLCV_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

logger = getLogger(__name__)


class Fetcher:
    def __init__(self, exchange: ccxt.Exchange, symbol: str) -> None:
        self._exchange = exchange
        self._symbol = symbol

    def fetch_symbol_info(self) -> dict:
        logger.info(
            f'Fetching symbol information from {self._exchange.name}...'
        )
        try:
            markets = self._exchange.load_markets()
            symbol_info = markets[self._symbol]
            logger.info('Symbol information fetched successfully')
            return symbol_info
        except Exception as e:
            logger.error(f'Failed to fetch symbol information: {e}')
            raise

    def fetch_historical_data(
        self,
        interval: str,
        start_time: str | None,
        limit: int | None,
    ) -> pd.Series:
        logger.info('Fetching historical data...')
        try:
            total_data = []
            since = self._exchange.parse8601(start_time)
            while True:
                partial_data = self._exchange.fetch_ohlcv(
                    symbol=self._symbol,
                    timeframe=interval,
                    since=since,
                    limit=limit,
                )
                if not partial_data:
                    break
                if total_data and total_data[-1][0] == partial_data[0][0]:
                    break
                total_data.extend(partial_data)
                since = partial_data[-1][0] + 1
            df = pd.DataFrame(data=total_data, columns=OHLCV_COLUMNS)
            close_data = df['close'].iloc[:-1].astype(float)
            logger.info('Historical data fetched successfully')
            return close_data
        except Exception as e:
            logger.error(f'Failed to fetch historical data: {e}')
            raise

    def fetch_position(self, symbol_info: dict, my_position: Position) -> None:
        logger.info('Fetching position information...')
        try:
            positions = self._exchange.fetch_positions(symbols=[self._symbol])
            if not positions:
                my_position.update(None)
                self._exchange.cancel_all_orders(self._symbol)
                logger.info(f"No active position for {symbol_info['id']}")
                return
            position = positions[0]
            amount = position['contracts']
            entry_price = position['entryPrice']
            side = Side(position['side'])
            my_position.update(side, amount, entry_price)
            logger.info(
                f"Current position:"
                f" {amount * side.sign()} {symbol_info['base']}"
                f" at {entry_price} {symbol_info['quote']}"
            )
        except Exception as e:
            logger.error(f'Failed to fetch position: {e}')
            raise

    def fetch_account_balance(self, symbol_info: dict) -> float:
        logger.info('Fetching account balance...')
        try:
            margin_asset = symbol_info['settle']
            account_info = self._exchange.fetch_balance()
            balance = account_info['total'][margin_asset]
            logger.info(f'Account balance: {balance} {margin_asset}')
            return balance
        except Exception as e:
            logger.error(f'Failed to fetch account balance: {e}')
            raise
