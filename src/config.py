"""Define a Config class that loads and manages configuration settings.

Typical usage example:

    config = Config()
    value = config.KEY
"""

from os import getenv
from typing import Any

import yaml


class Config:
    """Configuration settings.

    Load configuration from environment variables and YAML file.
    Support environment-specific settings and provide attribute access
    to configuration values.
    """

    def __init__(self) -> None:
        """Initialize the instance by loading config from YAML file."""
        self._env = getenv('ENVIRONMENT', 'production')
        config_dir = '.' if self._env == 'production' else '..'
        with open(f'{config_dir}/config.yaml', 'r') as f:
            self._config = yaml.safe_load(f)

    def __getattr__(self, name: str) -> Any:
        """Retrieve a configuration value.

        Check the value in environment variables first, then in the
        environment-specific config, and finally in the default config.

        Args:
            name: The name of the configuration value to retrieve.

        Returns:
            The value of the requested configuration item.

        Raises:
            AttributeError: Configuration item is not found.
        """
        if attr := getenv(name):
            return self._convert_type(attr)
        if name in self._config.get(self._env, {}):
            return self._config[self._env][name]
        if name in self._config['default']:
            return self._config['default'][name]
        raise AttributeError(f'{name} not set')

    @staticmethod
    def _convert_type(env: str) -> int | float | str:
        """Try to convert the input string to the appropriate type.

        Args:
            env: The value of the environment variable to convert.

        Returns:
            The value of the converted type if successful,
            otherwise the original string.
        """
        try:
            return int(env)
        except ValueError:
            try:
                return float(env)
            except ValueError:
                return env
