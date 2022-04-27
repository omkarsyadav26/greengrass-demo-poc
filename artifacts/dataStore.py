import json
import boto3
from tinydb import TinyDB, Query
from botocore.exceptions import ClientError
import datetime
import os

def insert_into_db(msg):
    db = TinyDB('db.json')
    User = Query()
    db.insert(msg)

def write_to_file(db):
    '''
    this function writes data to json from db
    '''
    time = datetime.datetime.now(datetime.timezone.utc)
    filename = 'stale-{}.json'.format(time.strftime("%Y-%m-%d-%H-%M-%S"))
    s3_location = '{}/{}'.format(time.strftime("%Y/%m/%d/%H"), filename)
    with open(filename, 'w') as f:
        json.dump(db.all(), f)
    db.truncate()
    return filename, s3_location


def upload_data_to_s3():
    '''
    this function will help to upload all stale data to s3
    '''
    db = TinyDB('db.json')
    User = Query()
    bucket = 'greengrass-poc-stream'
    if db.all():
        filename, s3_location = write_to_file(db)
        try:
            s3_client = boto3.client('s3')
            if os.path.exists(filename):
                response = s3_client.upload_file(filename, bucket, s3_location)
                print(response)
                os.remove(filename)
            else:
                print("The file does not exist")
        except ClientError as e:
            print("exception", e)