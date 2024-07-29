from __future__ import annotations

from enum import StrEnum


class Side(StrEnum):
    BUY = 'buy'
    SELL = 'sell'

    @classmethod
    def _missing_(cls, value: str) -> Side | None:
        if value == 'long':
            return cls.BUY
        if value == 'short':
            return cls.SELL
        return None

    def sign(self) -> int:
        return 1 if self == Side.BUY else -1
