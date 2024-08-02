"""Define a Side enum class that represents the order/position side."""

from __future__ import annotations

from enum import StrEnum


class Side(StrEnum):
    """An enumeration representing the side of an order or position.

    Attributes:
        BUY: Represent a buy order or long position.
        SELL: Represent a sell order or short position.
    """

    BUY = 'buy'
    SELL = 'sell'

    @classmethod
    def _missing_(cls, value: str) -> Side | None:
        """Handle alternative string representations of sides.

        Allow 'long' to be interpreted as BUY and 'short' as SELL.

        Args:
            value: The string value to interpret.

        Returns:
            The corresponding side, or None if no match is found.
        """
        if value == 'long':
            return cls.BUY
        if value == 'short':
            return cls.SELL
        return None

    def sign(self) -> int:
        """Determine the sign associated with the side.

        Returns:
            1 for buy/long, -1 for sell/short.
        """
        return 1 if self == Side.BUY else -1
