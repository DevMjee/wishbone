FROM public.ecr.aws/lambda/python:3.12

RUN microdnf install -y gcc libpq-devel && microdnf clean all

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY . ${LAMBDA_TASK_ROOT}

CMD ["historical_pipeline.lambda_handler"]

