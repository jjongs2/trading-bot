"""Define a Predictor class that makes prediction.

Typical usage example:

    predictor = Predictor(model, scaler)
    preprocessed_data = predictor.preprocess(ohlcv_data, window_size=5)
    predicted_data = predictor.predict(preprocessed_data)
"""

from logging import getLogger

import numpy as np
import tensorflow as tf
from numpy.lib.stride_tricks import sliding_window_view

logger = getLogger(__name__)


class Predictor:
    """Preprocess data and make predictions.

    Provide methods to preprocess time series data and make predictions
    using pre-trained deep learning models. Designed to work with keras
    models and scikit-learn scalers.
    """

    def __init__(self, model: tf.keras.Model, scalers: dict):
        """Initialize the instance with the model and scaler.

        Args:
            model: A pre-trained keras model for prediction.
            scaler: A fitted scaler for data normalization.
        """
        self._model = model
        self._scalers = scalers

    def preprocess(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """Preprocess the input time series data.

        Scale the data using the provided scalers, and reshape it into
        the format expected by the model.

        Args:
            data: A numpy array of time series data to preprocess.
            window_size: The size of the sliding window.

        Returns:
            A numpy array of preprocessed data ready to be entered into
            the model.
        """
        logger.info('Preprocessing data...')
        data_count, scaler_count = data.shape
        window_count = data_count - window_size + 1
        scaled_data = np.zeros_like(data)
        for i in range(scaler_count):
            column = data[:, i].reshape(data_count, 1)
            scaled_data[:, i] = self._scalers[i].transform(column).ravel()
        return sliding_window_view(
            scaled_data,
            window_shape=(window_size, scaler_count),
        ).reshape(window_count, window_size, scaler_count)

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """Make predictions using preprocessed input data.

        Use pre-trained model to make predictions on the input data, and
        then inverse transform the predictions to the original scale.

        Args:
            input_data: A numpy array of preprocessed data.

        Returns:
            A numpy array of closing price predictions in the original
            scale.
        """
        logger.info('Predicting...')
        prediction = self._model.predict(input_data)
        return self._scalers[3].inverse_transform(prediction).ravel()
