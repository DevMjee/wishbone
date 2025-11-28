"""Lambda function for the transform and load stages"""
from extract import extract_games
from transform import transform_all
from load import load_data


def lambda_handler(event, context):
    try:
        game_inputs = event.get('game_inputs')
        extract_games(game_inputs)
    except Exception as e:
        return {'status': 'error', 'msg': f'{str(e)} occurred in extract_gog'}
    try:
        transform_all()
    except Exception as e:
        return {'status': 'error', 'msg': f'{str(e)} occurred in transform'}
    try:
        load_data()
    except Exception as e:
        return {'status': 'error', 'msg': f'{str(e)} occurred in load'}

    return {'status': 'success', 'msg': 'RDS updated, pipeline successfully run'}


if __name__ == "__main__":
    pass
