import json
import boto3
from bson import json_util
from dataStore import insert_into_db

class MetaClass(type):
    """Singleton Design Pattern"""
    _instance = {} 
    def __call__(cls, *args, **kwargs):
        """ if instance already exist dont create one """
        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class KinesisFireHose(metaclass=MetaClass):

    def __init__(self, StreamName=None):
        self.streamName = StreamName
        try:
            self.client = boto3.client('firehose')
            print("Successfully created boto3 firehose client")
        except Exception as e:
            print("Failed to create boto3 firehose client. Error: " + str(e))
            exit(1)
    
    @property
    def describe(self):
        try:
            response = self.client.describe_delivery_stream(DeliveryStreamName = self.streamName, Limit=123)
            response_json = json.dumps(response, indent=3, default=json_util.default)
        except Exception as e:
            print("Failed to describe boto3 firehose. Error: " + str(e))
            response_json = json.dumps("error")
        return response_json

    def post(self, payload=None):
        print("\n\n\n\n")
        print("payload:---",type(payload),payload)
        json_payload=json.dumps(payload)
        print("json.dumps(payload)", json_payload)
        print("\n\n\n\n")
        json_payload += "\n"
        json_payload_encode = json_payload.encode("utf-8")
        try:
            response = self.client.put_record(DeliveryStreamName=self.streamName,Record={'Data': json.dumps(payload)})
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                # insert_into_db(json_payload_encode)
                insert_into_db(payload)
            response_aws = json.dumps(response, indent=3)
        except Exception as e:
            insert_into_db(payload)
            # insert_into_db(json_payload_encode)
            print("Failed to put record in boto3 firehose. Error: " + str(e))
            response_aws = json.dumps("error")
        return response_aws