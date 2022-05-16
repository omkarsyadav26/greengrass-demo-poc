import json
import boto3
import logging
import os


region = os.environ['AWS_REGION']
client = boto3.client('iot-data', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')


def get(event, context):
    # logging.info("request : {}".format(str(event)))
    try:
        data = client.get_thing_shadow(
            thingName='gpoc',
            shadowName='ACStatus'
        )
        data = json.loads((data["payload"]).read().decode("utf-8"))
        logging.info(data)
        return {
            'statusCode': 200,
            'body': json.dumps(data, default=str),
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
