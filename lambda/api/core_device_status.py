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
        # healthy_core_devices = client.list_core_devices(
        #     status='HEALTHY',
        #     maxResults=100,
        #     nextToken='string'
        # )
        # unhealthy_core_devices = client.list_core_devices(
        #     status='UNHEALTHY',
        #     maxResults=100,
        #     nextToken='string'
        # )
        # data = {
        #     'healthy': healthy_core_devices['coreDevices'],
        #     'unhealthy': unhealthy_core_devices['coreDevices']
        # }
        core_devices = client.list_core_devices()
        a = core_devices['coreDevices']
        for d in core_devices['coreDevices']:
            d['lastUpdateTs'] = d['lastStatusUpdateTimestamp'].timestamp()
            d.pop('lastStatusUpdateTimestamp')
            d['key'] = d.pop('status')
        data = {
            'data':  a
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
