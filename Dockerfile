FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

COPY src/* .
COPY config.yaml .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "lambda_function.lambda_handler" ]
