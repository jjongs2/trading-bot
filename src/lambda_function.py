from json import dumps
from logging import getLogger

import boto3
import ccxt

from config import Config
from trader_factory import create_trader

getLogger().setLevel('INFO')
logger = getLogger(__name__)


def lambda_handler(event, context):
    logger.info('Starting lambda_handler function...')
    try:
        config = Config()
        s3_client = boto3.client('s3')
        exchange_class = getattr(ccxt, config.EXCHANGE_ID)
        exchange = exchange_class(
            {
                'apiKey': config.EXCHANGE_API_KEY,
                'secret': config.EXCHANGE_API_SECRET,
                'options': {
                    'maxRetriesOnFailure': config.MAX_RETRIES,
                    'maxRetriesOnFailureDelay': config.RETRY_DELAY,
                },
            }
        )
        trader = create_trader(s3_client, exchange, config)
        trader.execute_trade()
        return {
            'statusCode': 200,
            'body': dumps('OK'),
        }
    except ccxt.NetworkError:
        raise
    except Exception as e:
        logger.exception(f'Exception raised in lambda_handler: {e}')
        return {
            'statusCode': 500,
            'body': dumps('Internal Server Error'),
        }
