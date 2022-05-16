import json
import boto3
import logging
import os
import uuid
from operator import itemgetter
from utils import json_response


region = os.environ['AWS_REGION']
client = boto3.client('greengrassv2', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')
client1 = boto3.client('iot', region_name=region)


def get(event, context):
    # logging.info("request : {}".format(str(event)))
    try:
        core_devices = client.list_core_devices()
        a = core_devices['coreDevices']
        for d in core_devices['coreDevices']:
            resp = client1.describe_thing(
                thingName=d['coreDeviceThingName']
            )
            d['id'] = {'id': str(uuid.uuid1())}
            if 'thingTypeName' in resp.keys():
                d['type'] = resp['thingTypeName']
            else:
                d['type'] = 'NA'
            d['label'] = resp['attributes']
            d.pop('lastStatusUpdateTimestamp')
            d.pop('status')
            d['name'] = d.pop('coreDeviceThingName')
        data = {
            'data':  a
        }
        # data = {
        #     'devices': list(map(itemgetter('coreDeviceThingName'), core_devices['coreDevices']))
        # }
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
