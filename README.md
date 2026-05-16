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

You need a pre-trained deep learning model and scalers. For more information, see [here](https://jjongs2.github.io/posts/trading-bot/).

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
  START_TIME: '2026-01-01T00:00:00Z'  # ISO 8601
```

- When setting `START_TIME`, please note that backtesting should be performed on data not used for model fitting to avoid overfitting.
- Make sure that `MODEL_KEY`, `SCALERS_KEY`, `DOWNLOAD_DIR` are set correctly so that the model and scalers can be loaded from the expected location.

Now run the simulator.

```bash
# Create a virtual environment
cd ~/trading-bot
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-local.txt

# Run in simulation mode
cd src
ENVIRONMENT=simulation python3.13 simulator.py
```

```
---------------------------  ------
           Number of trades      49
                   Win rate   55.1%
                  P&L ratio    2.45
Max profit rate (per trade)    8.8%
  Max loss rate (per trade)   -4.5%
              Final balance  1787.0
---------------------------  ------
```

<img src="https://dydi59svggub9.cloudfront.net/trading-bot/usdt-balance.png" alt="USDT balance" width="500">

### Live Trading

To deploy to AWS Lambda for serverless live trading:

1. Create an S3 bucket to store the model and scalers.
2. Create an ECR Repository to store Docker images.
3. Build and push the Docker image.
   - Can be done by manually running the workflow 'Manual deploy to Amazon ECR' in GitHub Actions.
4. Create a Lambda function using the Docker image pushed to ECR.
   - Please grant S3 access to the IAM role.
5. Set the configuration of your Lambda function.
   - Recommended general configuration
     - Memory: 1~2 GB
     - Timeout: 2 min
   - Required environment variables
     - `BUCKET_NAME`
     - `EXCHANGE_API_KEY`
     - `EXCHANGE_API_SECRET`
6. Create an EventBridge schedule to periodically invoke the Lambda function.

<br>

## Continuous Deployment

To set up CD:

1. Fork this repository.
2. Set up repository secrets for GitHub Actions in your repository settings.
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Update `cd.yml` with your AWS region, ECR repository name, and Lambda function name.
4. Push changes to `main` branch and activate the workflow.
