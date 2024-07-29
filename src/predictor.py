from logging import getLogger

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

logger = getLogger(__name__)


class Predictor:
    def __init__(
        self,
        model: tf.keras.Model,
        scaler: MinMaxScaler,
        window_size: int,
    ) -> None:
        self._model = model
        self._scaler = scaler
        self._window_size = window_size

    def preprocess(self, data: pd.Series) -> np.ndarray:
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
        logger.info('Predicting...')
        prediction = self._model.predict(input_data)[self._window_size - 1 :]
        return self._scaler.inverse_transform(prediction).ravel()
