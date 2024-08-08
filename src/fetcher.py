"""Define a Fetcher class that interacts with a crypto exchange.

Typical usage example:

    exchange = ccxt.binanceusdm()
    fetcher = Fetcher(exchange, 'BTC/USDT:USDT')
    symbol_info = fetcher.fetch_symbol_info()
    data = fetcher.fetch_historical_data(interval='1d', limit=15)
"""

from logging import getLogger

import ccxt
import numpy as np

from position import Position
from side import Side

logger = getLogger(__name__)


class Fetcher:
    """Fetch data from a crypto exchange.

    Provide methods to retrieve various types of data from the exchange.
    Designed to work with ccxt library.
    """

    def __init__(self, exchange: ccxt.Exchange, symbol: str):
        """Initialize the instance with an exchange and a symbol.

        Args:
            exchange: A ccxt.Exchange instance for the target exchange.
            symbol: The trading symbol to fetch data for.
        """
        self._exchange = exchange
        self._symbol = symbol

    def fetch_symbol_info(self) -> dict:
        """Fetch information about the trading symbol.

        Returns:
            A dict containing information about the trading symbol.

        Raises:
            Exception: An error occurred fetching symbol information.
        """
        logger.info(
            f'Fetching symbol information from {self._exchange.name}...'
        )
        try:
            markets = self._exchange.load_markets()
            symbol_info = markets[self._symbol]
            logger.info('Symbol information fetched successfully')
            return symbol_info
        except Exception as e:
            logger.error(f'Failed to fetch symbol information: {str(e)}')
            raise

    def fetch_historical_data(
        self,
        interval: str,
        start_time: str | None,
        limit: int | None = None,
    ) -> np.ndarray:
        """Fetch historical data for the symbol.

        Args:
            interval: The time interval for the data.
            start_time: The start time for the data in ISO 8601 format.
            limit: The maximum number of data to fetch.

        Returns:
            A numpy array of OHLCV data.

        Raises:
            Exception: An error occurred fetching historical data.
        """
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
            logger.info('Historical data fetched successfully')
            return np.array(total_data)[:-1, 1:]
        except Exception as e:
            logger.error(f'Failed to fetch historical data: {str(e)}')
            raise

    def fetch_position(self, symbol_info: dict, my_position: Position) -> None:
        """Fetch the position for the symbol and update Position object.

        Args:
            symbol_info: A dict containing symbol information.
            my_position: A Position object to update with fetched data.

        Raises:
            Exception: An error occurred fetching position information.
        """
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
            logger.error(f'Failed to fetch position: {str(e)}')
            raise

    def fetch_account_balance(self, symbol_info: dict) -> float:
        """Fetch the account balance for the symbol's margin asset.

        Args:
            symbol_info: A dict containing symbol information.

        Returns:
            The account balance for the margin asset.

        Raises:
            Exception: An error occurred fetching account balance.
        """
        logger.info('Fetching account balance...')
        try:
            margin_asset = symbol_info['settle']
            account_info = self._exchange.fetch_balance()
            balance = account_info['total'][margin_asset]
            logger.info(f'Account balance: {balance:.1f} {margin_asset}')
            return balance
        except Exception as e:
            logger.error(f'Failed to fetch account balance: {str(e)}')
            raise
