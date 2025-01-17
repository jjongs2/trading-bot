"""Define a factory function for creating Trader instances."""

import ccxt
from mypy_boto3_s3 import S3Client

from config import Config
from fetcher import Fetcher
from loader import Loader
from mock_s3client import MockS3Client
from orderer import Orderer
from position import Position
from predictor import Predictor
from strategy import MyStrategy
from trader import Trader


def create_trader(
    s3_client: S3Client | MockS3Client,
    exchange: ccxt.Exchange,
    config: Config = Config(),
) -> Trader:
    """Create and return a configured Trader instance.

    Initialize all the components needed for the trading system and
    combine them into a Trader instance.

    Args:
        s3_client:
            An (Mock)S3Client for loading the model and scaler.
        exchange:
            An ccxt.Exchange instance for interacting with the exchange.
        config:
            A Config instance containing configuration parameters.

    Returns:
        A configured Trader instance ready for executing trades.

    Raises:
        Exception: Not enough historical data for prediction.
    """
    position = Position()
    strategy = MyStrategy(config.THRESHOLD, config.STOP_LOSS)

    loader = Loader(s3_client, config.BUCKET_NAME, config.DOWNLOAD_DIR)
    fetcher = Fetcher(exchange, config.SYMBOL)
    orderer = Orderer(exchange, config.SYMBOL)

    model = loader.load_model(config.MODEL_KEY)
    scaler = loader.load_scalers(config.SCALERS_KEY)
    predictor = Predictor(model, scaler)

    symbol_info = fetcher.fetch_symbol_info()

    start_time = getattr(config, 'START_TIME', None)
    limit = None if start_time else config.WINDOW_SIZE + 1
    historical_data = fetcher.fetch_historical_data(
        interval=config.INTERVAL,
        start_time=start_time,
        limit=limit,
    )
    preprocessed_data = predictor.preprocess(
        data=historical_data,
        window_size=config.WINDOW_SIZE,
    )
    predicted_prices = predictor.predict(preprocessed_data)
    historical_prices = historical_data[config.WINDOW_SIZE - 1 :, 3]

    return Trader(
        config=config,
        fetcher=fetcher,
        orderer=orderer,
        position=position,
        strategy=strategy,
        symbol_info=symbol_info,
        historical_prices=historical_prices,
        predicted_prices=predicted_prices,
    )
