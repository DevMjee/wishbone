"""Lambda function for creating and sending emails about discounts using SES"""


def lambda_handler(event, context):
    return {'event': event, 'context': context}


if __name__ == "__main__":
    pass
