"""Define a Loader class that handles the loading of a model and scaler

Typical usage example:

    loader = Loader(s3_client, 'YOUR_BUCKET_NAME', '/tmp')
    model = loader.load_model('model.keras')
    scaler = loader.load_scaler('scaler.pkl')
"""

from logging import getLogger
from pickle import load

import tensorflow as tf
from mypy_boto3_s3 import S3Client
from sklearn.preprocessing import MinMaxScaler

from mock_s3client import MockS3Client

logger = getLogger(__name__)


class Loader:
    """Load the model and scaler.

    Provide methods to load the keras model and scikit-learn scaler from
    an S3 bucket or local file system. Support both real S3 client and
    mock client for simulation.
    """

    def __init__(
        self,
        s3_client: S3Client | MockS3Client,
        bucket_name: str,
        download_dir: str,
    ):
        """Initialize the instance with S3 client and storage info.

        Args:
            s3_client: An instance of S3Client or MockS3Client.
            bucket_name: The name of the S3 bucket to load from.
            download_dir: The local directory to store downloaded files.
        """
        self._s3_client = s3_client
        self._bucket_name = bucket_name
        self._download_dir = download_dir

    def load_model(self, key: str) -> tf.keras.Model:
        """Load the keras model from S3 or local storage.

        Args:
            key: The filename of the model to load.

        Returns:
            An instance of the model.

        Raises:
            Exception: An error occurred loading the model.
        """
        try:
            path = self._download_file(key)
            model = tf.keras.models.load_model(path)
            logger.info(f'{key} loaded successfully')
            return model
        except Exception as e:
            logger.error(f'Failed to load {key}: {e}')
            raise

    def load_scaler(self, key: str) -> MinMaxScaler:
        """Load the scikit-learn scaler from S3 or local storage.

        Args:
            key: The S3 key or local filename of the scaler to load.

        Returns:
            An instance of the scaler.

        Raises:
            Exception: An error occurred loading the scaler.
        """
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
        """Download the file from S3 to local storage.

        Args:
            key: The S3 key of the file to download.

        Returns:
            The local path of the downloaded file.

        Raises:
            Exception: An error occurred downloading the file.
        """
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
