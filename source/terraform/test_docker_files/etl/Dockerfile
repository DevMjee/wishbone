from public.ecr.aws/lambda/python:3.12

workdir ${LAMBDA_TASK_ROOT}

copy requirements.txt .
run pip3 install -r requirements.txt

copy test_etl_lambda.py ${LAMBDA_TASK_ROOT}

cmd ["test_etl_lambda.lambda_handler"]