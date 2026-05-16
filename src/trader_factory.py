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


def init_components(
    s3_client: S3Client | MockS3Client,
    exchange: ccxt.Exchange,
    config: Config = Config(),
) -> tuple[Fetcher, Orderer, Predictor, dict]:
    """Build reusable components: load model and fetch symbol info.

    Intended to run once at module import time (Lambda init phase) so
    that S3 downloads and TensorFlow model loading happen before any
    invocation begins.

    Args:
        s3_client:
            An (Mock)S3Client for loading the model and scaler.
        exchange:
            An ccxt.Exchange instance for interacting with the exchange.
        config:
            A Config instance containing configuration parameters.

    Returns:
        A tuple of (fetcher, orderer, predictor, symbol_info).
    """
    fetcher = Fetcher(exchange, config.SYMBOL)
    orderer = Orderer(exchange, config.SYMBOL)

    loader = Loader(s3_client, config.BUCKET_NAME, config.DOWNLOAD_DIR)
    model = loader.load_model(config.MODEL_KEY)
    scalers = loader.load_scalers(config.SCALERS_KEY)
    predictor = Predictor(model, scalers)

    symbol_info = fetcher.fetch_symbol_info()
    return fetcher, orderer, predictor, symbol_info


def build_trader(
    fetcher: Fetcher,
    orderer: Orderer,
    predictor: Predictor,
    symbol_info: dict,
    config: Config = Config(),
) -> Trader:
    """Build a Trader using prebuilt components and fresh market data.

    Fetch the latest historical data and run a prediction so the
    returned Trader reflects the current market.

    Args:
        fetcher: A Fetcher built by init_components.
        orderer: An Orderer built by init_components.
        predictor: A Predictor built by init_components.
        symbol_info: Symbol info fetched by init_components.
        config: A Config instance containing configuration parameters.

    Returns:
        A configured Trader instance ready for executing trades.

    Raises:
        Exception: Not enough historical data for prediction.
    """
    position = Position()
    strategy = MyStrategy(config.THRESHOLD, config.STOP_LOSS)

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
    fetcher, orderer, predictor, symbol_info = init_components(
        s3_client, exchange, config
    )
    return build_trader(fetcher, orderer, predictor, symbol_info, config)
