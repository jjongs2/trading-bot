from os import getenv
from typing import Any

import yaml


class Config:
    def __init__(self) -> None:
        self._env = getenv('ENVIRONMENT', 'production')
        config_dir = '.' if self._env == 'production' else '..'
        with open(f'{config_dir}/config.yaml', 'r') as f:
            self._config = yaml.safe_load(f)

    def __getattr__(self, name: str) -> Any:
        if attr := getenv(name):
            return self._convert_type(attr)
        if name in self._config.get(self._env, {}):
            return self._config[self._env][name]
        if name in self._config['default']:
            return self._config['default'][name]
        raise AttributeError(f'{name} not set')

    @staticmethod
    def _convert_type(env: str) -> int | float | str:
        try:
            return int(env)
        except ValueError:
            try:
                return float(env)
            except ValueError:
                return env
