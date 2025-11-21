from public.ecr.aws/lambda/python:3.12

workdir ${LAMBDA_TASK_ROOT}

copy requirements.txt .
run pip3 install -r requirements.txt

copy assess_price_history_lambda.py ${LAMBDA_TASK_ROOT}

cmd ["assess_price_history_lambda.lambda_handler"]