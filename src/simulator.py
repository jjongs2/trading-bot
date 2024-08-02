"""Define a Simulator class for backtesting trading strategies."""

import logging

from tabulate import tabulate

from mock_exchange import MockExchange
from mock_s3client import MockS3Client
from trader_factory import create_trader

logging.basicConfig(level='WARNING')


class Simulator:
    """Simulate trading strategies.

    Set up a simulated trading environment. Provide methods to run
    simulations and evaluate the results.
    """

    def __init__(self):
        """Initialize the instance with a mock exchange and a trader."""
        self._exchange = MockExchange()
        self._trader = create_trader(MockS3Client(), self._exchange)

    def run(self):
        """Run trade simulations.

        Simulate the trading process by iterating over historical data
        from the mock exchange, calling Trader's execute_trade method at
        each time step.
        """
        while (time_index := self._exchange.next()) is not None:
            self._trader.execute_trade(time_index)

    def evaluate(self):
        """Evaluate the performance of the trading strategy.

        Call MockExchange's pnl_analysis method to generate performance
        metrics for the simulated trading session.

        Returns:
            A dict containing various metrics.
        """
        return self._exchange.pnl_analysis()


if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()
    result = simulator.evaluate()
    if result:
        print(tabulate(result.items(), colalign=('right', 'right')))
    else:
        print('No transaction occurred.')
