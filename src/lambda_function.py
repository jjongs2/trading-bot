"""Serve as an entry point for AWS Lambda function.

Designed to be triggered periodically (by Amazon EventBridge) to
regularly evaluate market conditions and make trade decisions based on
the implemented strategy.

Note:
    The exchange API credentials and s3 bucket name must be set in the
    AWS Lambda environment variables.
"""

from json import dumps
from logging import getLogger

import boto3
import ccxt

from config import Config
from trader_factory import create_trader

getLogger().setLevel('INFO')
logger = getLogger(__name__)


def lambda_handler(event, context):
    """Handler for AWS Lambda function.

    Connect to the exchange client, create a trader instance and execute
    a single trade decision.

    Args:
        event:
            A dict containing data to be processed by Lambda function.
            Not used in this implementation but required by AWS Lambda.
        context:
            A context object containing methods and properties that
            provide information about the invocation, function, and
            execution environment. Not used in this implementation but
            required by AWS Lambda.

    Returns:
        A dict containing status code and response body.

    Raises:
        ccxt.NetworkError:
            A network-related error occurred when connecting to the
            exchange. Re-raised to allow AWS Lambda to retry the
            function execution.
    """
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
        # Re-raise network errors to allow AWS Lambda to retry
        raise
    except Exception as e:
        logger.exception(f'Exception raised in lambda_handler: {e}')
        return {
            'statusCode': 500,
            'body': dumps('Internal Server Error'),
        }
