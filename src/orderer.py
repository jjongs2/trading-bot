"""Define an Orderer class that places orders on a crypto exchange.

Typical usage example:

    orderer = Orderer(exchange, 'BTC/USDT:USDT')
    orderer.place_order(Side.BUY, 0.1, 50000.0)
"""

from logging import getLogger

import ccxt

from side import Side

logger = getLogger(__name__)


class Orderer:
    """Place an order on a crypto exchange.

    Handle the details of order creation and provide logging for order
    placement results. Designed to work with ccxt library.
    """

    def __init__(self, exchange: ccxt.Exchange, symbol: str) -> None:
        """Initialize the instance with an exchange and a symbol.

        Args:
            exchange: A ccxt.Exchange instance for the target exchange.
            symbol: The trading symbol to place an order for.
        """
        self._exchange = exchange
        self._symbol = symbol

    def place_order(
        self,
        side: Side,
        amount: float,
        current_price: float,
    ) -> None:
        """Place a limit order on the exchange.

        Args:
            side: The side of the order.
            amount: The amount of the base asset to trade.
            current_price: The price at which to place the limit order.

        Raises:
            Exception: An error occurred placing the order.
        """
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
            logger.error(f'Failed to place order: {str(e)}')
            raise
