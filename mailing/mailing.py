"""Lambda function checking for extracting the latest discounts from the S3"""


def lambda_handler(event, context):
    return {'event': event, 'context': context}


if __name__ == "__main__":
    pass
