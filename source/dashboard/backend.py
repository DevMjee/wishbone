import aioboto3
import json
import asyncio


async def trigger_lambda(payload: dict) -> dict:
    async with aioboto3.client('lambda') as client:
        response = await client.invoke(
            FunctionName='wishbone-tracking-lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

    response_payload = await response['Payload'].read()
    return json.loads(response_payload)


def run_unsubscribe(email: str):
    payload = {
        'subscribe': 'False',
        'email': email
    }
    return asyncio.run(trigger_lambda(payload))


def run_subscribe(email: str, game_id):
    payload = {
        'subscribe': 'True',
        'email': email,
        'game_id': str(game_id)
    }
    return asyncio.run(trigger_lambda(payload))
