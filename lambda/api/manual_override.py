import json
import boto3
import logging
import os
from operator import itemgetter
from utils import json_response


region = os.environ['AWS_REGION']
client = boto3.client('iot-data', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')

# {
#     "manualOverride": "on/off",
#     "acStatus": "on/off"
# }


def post(event, context):
    try:
        body = json.loads(event['body'])
        if ('manualOverride' in body.keys()) or ('acStatus' in body.keys()):
            client.publish(
                topic='updatetopic',
                qos=0,
                retain=False,
                payload=json.dumps(body).encode('utf-8')
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'success'}, default=str),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            }
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'invalid body'}, default=str),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 404,
            'body': json.dumps(e),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
