import json
import boto3
import logging
import uuid
import os
from operator import itemgetter
from utils import json_response


region = os.environ['AWS_REGION']
client = boto3.client('iot', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')


def get(event, context):
    # logging.info("request : {}".format(str(event)))
    try:
        # core_devices = client.list_core_devices()
        # data = {
        #     'devices': list(map(itemgetter('coreDeviceThingName'), core_devices['coreDevices']))
        # }
        resp = client.list_things()
        a = resp['things']
        for d in resp['things']:
            d['id'] = {'id': str(uuid.uuid1())}
            if 'thingTypeName' in d.keys():
                d['type'] = d.pop('thingTypeName')
            else:
                d['type'] = 'NA'
            d['label'] = d.pop('attributes')
            d.pop('version')
            d.pop('thingArn')
            d['name'] = d.pop('thingName')
        data = {
            'data':  a
        }
        logging.info(data)
        return {
            'statusCode': 200,
            'body': json.dumps(data),
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
