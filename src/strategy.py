"""Define abstract and concrete strategy classes."""

from abc import ABC, abstractmethod

from position import Position


class Strategy(ABC):
    """An abstract base class for trading strategies."""

    @abstractmethod
    def should_open_position(self, *args, **kwargs) -> bool:
        """Determine whether a new position should be opened."""
        pass

    @abstractmethod
    def should_close_position(self, *args, **kwargs) -> bool:
        """Determine whether an existing position should be closed."""
        pass


class MyStrategy(Strategy):
    """An example of a specific implementation of a trading strategy.

    Implement a specific trading strategy based on price thresholds and
    stop loss conditions.
    """

    def __init__(self, threshold: float, stop_loss: float):
        """Initialize the instance with a threshold and stop loss value.

        Args:
            threshold:
                The price change threshold for opening a position.
            stop_loss:
                The stop loss threshold for closing a position.
        """
        self._threshold = threshold
        self._stop_loss = stop_loss

    def should_open_position(
        self,
        current_price: float,
        predicted_price: float,
    ) -> bool:
        """Determine whether a new position should be opened.

        Calculate the predicted price change and compare it to the
        threshold.

        Args:
            current_price: The current price of the base asset.
            predicted_price: The predicted next price of the base asset.

        Returns:
            True if a new position should be opened, False otherwise.
        """
        price_change_rate = (predicted_price - current_price) / current_price
        return abs(price_change_rate) > self._threshold

    def should_close_position(
        self,
        position: Position,
        current_price: float,
        predicted_price: float,
    ) -> bool:
        """Determine whether an existing position should be closed.

        Compare the predicted price to the current price and check if
        the current price reached stop loss.

        Args:
            position: The current trading position.
            current_price: The current price of the base asset.
            predicted_price: The predicted next price of the base asset.

        Returns:
            True if the position should be closed, False otherwise.
        """
        entry_price = position.entry_price
        if position.is_long():
            return (
                predicted_price < current_price
                or current_price < entry_price * (1 - self._stop_loss)
            )
        return (
            predicted_price > current_price
            or current_price > entry_price * (1 + self._stop_loss)
        )
