from side import Side


class Position:
    def __init__(
        self,
        side: Side | None = None,
        amount: float = 0.0,
        entry_price: float = 0.0,
        entry_time: str = '',
    ) -> None:
        self._side = side
        self._amount = amount
        self._entry_price = entry_price
        self._entry_time = entry_time

    @property
    def side(self) -> Side | None:
        return self._side

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def entry_price(self) -> float:
        return self._entry_price

    @property
    def entry_time(self) -> str:
        return self._entry_time

    def is_long(self) -> bool:
        return self._side == Side.BUY

    def is_none(self) -> bool:
        return self._side is None

    def is_short(self) -> bool:
        return self._side == Side.SELL

    def inverse(self) -> Side:
        return Side.SELL if self.is_long() else Side.BUY

    def update(
        self,
        side: Side | None,
        amount: float = 0.0,
        entry_price: float = 0.0,
        entry_time: str = '',
    ) -> None:
        self._side = side
        self._amount = amount
        self._entry_price = entry_price
        self._entry_time = entry_time

    def close(self) -> None:
        self.update(None)
