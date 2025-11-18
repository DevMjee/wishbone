"""Lambda function for deleting user personal data upon request"""


def lambda_handler(event, context):
    return {'event': event, 'context': context}


if __name__ == "__main__":
    pass
