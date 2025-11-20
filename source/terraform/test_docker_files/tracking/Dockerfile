FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY assess_tracking_lambda.py .

CMD [ "assess_tracking_lambda.lambda_handler" ]