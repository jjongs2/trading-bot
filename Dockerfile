FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.13

WORKDIR /var/task

COPY src/* .
COPY config.yaml .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "lambda_function.lambda_handler" ]
