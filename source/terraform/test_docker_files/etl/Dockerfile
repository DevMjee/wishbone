from public.ecr.aws/lambda/python:3.12

workdir ${LAMBDA_TASK_ROOT}

copy requirements.txt .
run pip3 install -r requirements.txt

copy assess_etl_lambda.py ${LAMBDA_TASK_ROOT}

cmd ["assess_etl_lambda.lambda_handler"]