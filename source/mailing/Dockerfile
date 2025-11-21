FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY html_email.py .
COPY mailing.py .

CMD [ "mailing.lambda_handler" ]