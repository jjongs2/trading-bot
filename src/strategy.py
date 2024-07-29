from abc import ABC, abstractmethod

from position import Position


class Strategy(ABC):
    @abstractmethod
    def should_open_position(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def should_close_position(self, *args, **kwargs) -> bool:
        pass


class MyStrategy(Strategy):
    def __init__(self, threshold: float, stop_loss: float) -> None:
        self._threshold = threshold
        self._stop_loss = stop_loss

    def should_open_position(
        self,
        current_price: float,
        predicted_price: float,
    ) -> bool:
        price_change_rate = (predicted_price - current_price) / current_price
        return abs(price_change_rate) > self._threshold

    def should_close_position(
        self,
        position: Position,
        current_price: float,
        predicted_price: float,
    ) -> bool:
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
