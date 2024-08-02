"""Define a Position class that represents a trading position."""

from side import Side


class Position:
    """A trading position.

    Encapsulate the essential attributes of a position.
    Provide methods to get or update the position's state.
    """

    def __init__(
        self,
        side: Side | None = None,
        amount: float = 0.0,
        entry_price: float = 0.0,
        entry_time: str = '',
    ) -> None:
        """Initialize the instance with the given values.

        Args:
            side: The side of the position.
            amount: The amount of the base asset in the position.
            entry_price: The price at which the position was opened.
            entry_time: The time at which the position was opened.
        """
        self._side = side
        self._amount = amount
        self._entry_price = entry_price
        self._entry_time = entry_time

    @property
    def side(self) -> Side | None:
        """Get the side of the position."""
        return self._side

    @property
    def amount(self) -> float:
        """Get the amount of the base asset in the position."""
        return self._amount

    @property
    def entry_price(self) -> float:
        """Get the entry price of the position."""
        return self._entry_price

    @property
    def entry_time(self) -> str:
        """Get the entry time of the position."""
        return self._entry_time

    def is_long(self) -> bool:
        """Check if the position is a long position.

        Returns:
            True if the position is long, False otherwise.
        """
        return self._side == Side.BUY

    def is_none(self) -> bool:
        """Check if the position is empty.

        Returns:
            True if there is no active position, False otherwise.
        """
        return self._side is None

    def is_short(self) -> bool:
        """Check if the position is a short position.

        Returns:
            True if the position is short, False otherwise.
        """
        return self._side == Side.SELL

    def inverse(self) -> Side:
        """Get the opposite side of the current position.

        Returns:
            Opposite side.
        """
        return Side.SELL if self.is_long() else Side.BUY

    def update(
        self,
        side: Side | None,
        amount: float = 0.0,
        entry_price: float = 0.0,
        entry_time: str = '',
    ) -> None:
        """Update the position with new values.

        Args:
            side: The new side of the position.
            amount: The new amount of the base asset in the position.
            entry_price: The new entry price of the position.
            entry_time: The new entry time of the position.
        """
        self._side = side
        self._amount = amount
        self._entry_price = entry_price
        self._entry_time = entry_time

    def close(self) -> None:
        """Close the current position by setting its side to None."""
        self.update(None)
