import json
import boto3
import logging
import os
from operator import itemgetter
from utils import json_response


region = os.environ['AWS_REGION']
client = boto3.client('greengrassv2', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')


def get(event, context):
    # logging.info("request : {}".format(str(event)))
    try:
        core_devices = client.list_core_devices()
        data = {
            'devices':  core_devices['coreDevices']
        }
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
