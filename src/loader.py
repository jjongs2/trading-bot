from logging import getLogger
from pickle import load

import tensorflow as tf
from mypy_boto3_s3 import S3Client
from sklearn.preprocessing import MinMaxScaler

from mock_s3client import MockS3Client

logger = getLogger(__name__)


class Loader:
    def __init__(
        self,
        s3_client: S3Client | MockS3Client,
        bucket_name: str,
        download_dir: str,
    ):
        self._s3_client = s3_client
        self._bucket_name = bucket_name
        self._download_dir = download_dir

    def load_model(self, key: str) -> tf.keras.Model:
        try:
            path = self._download_file(key)
            model = tf.keras.models.load_model(path)
            logger.info(f'{key} loaded successfully')
            return model
        except Exception as e:
            logger.error(f'Failed to load {key}: {e}')
            raise

    def load_scaler(self, key: str) -> MinMaxScaler:
        try:
            path = self._download_file(key)
            with open(path, 'rb') as f:
                scaler = load(f)
            logger.info(f'{key} loaded successfully')
            return scaler
        except Exception as e:
            logger.error(f'Failed to load {key}: {e}')
            raise

    def _download_file(self, key: str) -> str:
        logger.info(f'Loading {key}...')
        try:
            download_path = f'{self._download_dir}/{key}'
            self._s3_client.download_file(
                Bucket=self._bucket_name,
                Key=key,
                Filename=download_path,
            )
            return download_path
        except Exception as e:
            logger.error(f'Failed to download {key}: {e}')
            raise
