FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY transform.py load.py transform_load.py ./

CMD [ "transform_load.lambda_handler" ]