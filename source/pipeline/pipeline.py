"""Lambda function for the transform and load stages"""
from extract_gog import extract_gog
from extract_steam import export_steam
from transform import transform_all
from load import load_data


def lambda_handler(event, context):
    try:
        extract_gog()
    except Exception as e:
        return {'status': 'error', 'msg': f'{str(e)} occurred in extract_gog'}
    try:
        export_steam()
    except Exception as e:
        return {'status': 'error', 'msg': f'{str(e)} occurred in extract_steam'}
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
