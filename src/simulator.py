import logging

from tabulate import tabulate

from mock_exchange import MockExchange
from mock_s3client import MockS3Client
from trader_factory import create_trader

logging.basicConfig(level='WARNING')


class Simulator:
    def __init__(self):
        self._exchange = MockExchange()
        self._trader = create_trader(MockS3Client(), self._exchange)

    def run(self):
        while (time_index := self._exchange.next()) is not None:
            self._trader.execute_trade(time_index)

    def evaluate(self):
        return self._exchange.pnl_analysis()


if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()
    result = simulator.evaluate()
    if result:
        print(tabulate(result.items(), colalign=('right', 'right')))
    else:
        print('No transaction occurred.')
