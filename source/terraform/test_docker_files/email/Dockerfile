from public.ecr.aws/lambda/python:3.12

workdir ${LAMBDA_TASK_ROOT}

copy requirements.txt .
run pip3 install -r requirements.txt

copy assess_email_lambda.py ${LAMBDA_TASK_ROOT}

cmd ["assess_email_lambda.lambda_handler"]