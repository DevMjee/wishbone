"""Lambda function for the transform and load stages"""


def lambda_handler(event, context):
    return {'event': event, 'context': context}


if __name__ == "__main__":
    pass
