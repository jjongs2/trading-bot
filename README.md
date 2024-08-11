# Trading Bot

A serverless cryptocurrency trading bot that predicts price movements using deep learning models and executes trades

### Features

- Support for multiple cryptocurrency exchanges via [CCXT](https://github.com/ccxt/ccxt) library
- Use pre-trained deep learning models for price prediction
- Provide backtesting capabilities for trading strategy evaluation
- Utilize serverless architecture with [AWS Lambda](https://aws.amazon.com/lambda/)
- Continuous deployment with [GitHub Actions](https://github.com/features/actions)

<br>

## Prerequisites

You need a pre-trained deep learning model and scalers.

<br>

## Usage

You can implement your own trading strategy by modifying `MyStrategy` class, or adding a new class that inherits from `Strategy` class.

```python
class Strategy(ABC):
    @abstractmethod
    def should_open_position(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def should_close_position(self, *args, **kwargs) -> bool:
        pass
```

### Backtesting

Set up the configuration in `config.yaml`.

```yaml
default:
  EXCHANGE_ID: 'binanceusdm'
  INTERVAL: '1d'
  LEVERAGE: 1
  MIN_ORDER_AMOUNT: 0.002
  MODEL_KEY: 'model.keras'
  SCALERS_KEY: 'scalers.pkl'
  STOP_LOSS: 0.00         # 0.01 = 1%
  SYMBOL: 'BTC/USDT:USDT'
  THRESHOLD: 0.00         # 0.01 = 1%
  WINDOW_SIZE: 5

simulation:
  BUCKET_NAME: ''                     # No need to change
  DOWNLOAD_DIR: '../downloads'        # Path to model and scalers
  START_TIME: '2024-02-12T00:00:00Z'  # ISO 8601
```

When setting `START_TIME`, please note that backtesting should be performed on data not used for model fitting to avoid overfitting.

Now run the simulator.

```bash
(env) user@host:~/trading-bot$ pip install -r requirements-local.txt
(env) user@host:~/trading-bot$ export ENVIRONMENT=simulation
(env) user@host:~/trading-bot$ cd src
(env) user@host:~/trading-bot/src$ python simulator.py
```

```bash
---------------------------  ------
           Number of trades      64
                   Win rate   51.6%
                  P&L ratio    1.72
Max profit rate (per trade)    9.5%
  Max loss rate (per trade)   -5.1%
              Final balance  1524.2
---------------------------  ------
```

<img src="https://dydi59svggub9.cloudfront.net/trading-bot/usdt-balance.png" width="500">

### Live Trading

To deploy to AWS Lambda for serverless live trading:

1. Create an S3 bucket to store the model and scalers.
2. Create an ECR Repository to store Docker images.
3. Build and push the Docker image (can be done by manually running the workflow 'Manual deploy to Amazon ECR' in GitHub Actions).
4. Create a Lambda function using the Docker image pushed to ECR.
5. Set the required environment variables in your Lambda function configuration.
   - `BUCKET_NAME`
   - `EXCHANGE_API_KEY`
   - `EXCHANGE_API_SECRET`
6. Create an EventBridge rule to periodically execute the Lambda function.

<br>

## Continuous Deployment

To set up CD:

1. Fork this repository.
2. Set up repository secrets for GitHub Actions in your repository settings.
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Update `cd.yml` with your AWS region, ECR repository name, and Lambda function name.
4. Push changes to `main` branch and activate the workflow.
