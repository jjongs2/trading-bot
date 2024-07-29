from logging import getLogger

import ccxt

from side import Side

logger = getLogger(__name__)


class Orderer:
    def __init__(self, exchange: ccxt.Exchange, symbol: str) -> None:
        self._exchange = exchange
        self._symbol = symbol

    def place_order(
        self,
        side: Side,
        amount: float,
        current_price: float,
    ) -> None:
        logger.info(f'Attempting to place {side} order...')
        try:
            order = self._exchange.create_order(
                symbol=self._symbol,
                type='limit',
                side=side,
                amount=amount,
                price=current_price,
            )
            logger.info(f'Order placed successfully:\n{order}')
        except Exception as e:
            logger.error(f'Failed to place order: {e}')
            raise
