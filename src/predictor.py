"""Define a Predictor class that makes prediction.

Typical usage example:

    predictor = Predictor(model, scaler, window_size=5)
    preprocessed_data = predictor.preprocess(historical_data)
    predicted_data = predictor.predict(preprocessed_data)
"""

from logging import getLogger

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

logger = getLogger(__name__)


class Predictor:
    """Preprocess data and make predictions.

    Provide methods to preprocess time series data and make predictions
    using pre-trained deep learning models. Designed to work with keras
    models and scikit-learn scalers.
    """

    def __init__(
        self,
        model: tf.keras.Model,
        scaler: MinMaxScaler,
        window_size: int,
    ):
        """Initialize the instance with the model and scaler.

        Args:
            model: A pre-trained keras model for prediction.
            scaler: A fitted scaler for data normalization.
            window_size: The size of the rolling window for smoothing.
        """
        self._model = model
        self._scaler = scaler
        self._window_size = window_size

    def preprocess(self, data: pd.Series) -> np.ndarray:
        """Preprocess the input time series data.

        Use the rolling window to apply smoothing, scale the data using
        the provided scaler, and reshape it into the format expected by
        the model.

        Args:
            data:
                A pandas Series containing time series data to
                preprocess.

        Returns:
            A numpy array of preprocessed data ready to be entered into
            the model.
        """
        logger.info('Preprocessing data...')
        smoothed_data = data.rolling(self._window_size).mean()
        reshaped_data = smoothed_data.to_numpy().reshape(-1, 1)
        scaled_data = self._scaler.transform(reshaped_data)
        window_count = len(data) - self._window_size + 1
        result = np.zeros((window_count, self._window_size, 1))
        for i in range(window_count):
            result[i, :, 0] = scaled_data[i : i + self._window_size, 0]
        return result

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """Make predictions using preprocessed input data.

        Use pre-trained model to make predictions on the input data, and
        then inverse transform the predictions to the original scale.

        Args:
            input_data: A numpy array of preprocessed data.

        Returns:
            A numpy array of predictions in the original scale.
        """
        logger.info('Predicting...')
        prediction = self._model.predict(input_data)[self._window_size - 1 :]
        return self._scaler.inverse_transform(prediction).ravel()
