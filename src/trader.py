from logging import getLogger

import numpy as np
import pandas as pd

from config import Config
from fetcher import Fetcher
from orderer import Orderer
from position import Position
from side import Side
from strategy import Strategy

logger = getLogger(__name__)


class Trader:
    def __init__(
        self,
        config: Config,
        fetcher: Fetcher,
        orderer: Orderer,
        position: Position,
        strategy: Strategy,
        symbol_info: dict,
        historical_data: pd.Series,
        predicted_data: np.ndarray,
    ) -> None:
        self._config = config
        self._fetcher = fetcher
        self._orderer = orderer
        self._position = position
        self._strategy = strategy
        self._symbol_info = symbol_info
        self._historical_data = historical_data
        self._predicted_data = predicted_data

    def execute_trade(self, time_index: int = -1) -> None:
        self._fetcher.fetch_position(self._symbol_info, self._position)
        current_price = self._historical_data.iloc[time_index].item()
        predicted_price = self._predicted_data.item(time_index)
        logger.info(
            f"[{self._symbol_info['id']}]"
            f" Current price: {current_price:.1f}"
            f", Predicted price: {predicted_price:.1f}"
        )
        if self._position.is_none():
            self._open_position_if(current_price, predicted_price)
        else:
            self._close_position_if(current_price, predicted_price)

    def _open_position_if(
        self,
        current_price: float,
        predicted_price: float,
    ) -> None:
        logger.info('Evaluating whether to open position...')
        if self._strategy.should_open_position(current_price, predicted_price):
            side = Side.BUY if current_price < predicted_price else Side.SELL
            logger.info(f'Conditions met to open {side} position')
            self._open_position(side, current_price)
        else:
            logger.info('Conditions not met to open position')

    def _open_position(self, side: Side, current_price: float) -> None:
        balance = self._fetcher.fetch_account_balance(self._symbol_info)
        amount_precision = self._symbol_info['precision']['amount']
        amount = round(
            number=(balance * self._config.LEVERAGE) / current_price,
            ndigits=-np.log10(amount_precision).astype(int),
        )
        if amount < self._config.MIN_ORDER_AMOUNT:
            logger.warning('Not enough balance to open position')
            return
        self._orderer.place_order(side, amount, current_price)

    def _close_position_if(
        self,
        current_price: float,
        predicted_price: float,
    ) -> None:
        logger.info(
            f'Evaluating whether to close {self._position.side} position...'
        )
        if self._strategy.should_close_position(
            self._position, current_price, predicted_price
        ):
            logger.info('Conditions met to close position')
            self._close_position(current_price)
        else:
            logger.info('Conditions not met to close position')

    def _close_position(self, current_price: float) -> None:
        side = self._position.inverse()
        amount = self._position.amount
        self._orderer.place_order(side, amount, current_price)
