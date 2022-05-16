import boto3
import logging
import json
import os
import urllib.parse

region = os.environ['AWS_REGION']
client = boto3.client('athena', region_name=region)
logging.getLogger().setLevel(logging.INFO)
logging.info('Loading  get core device details lambda function')


def query_exec(client):
    response = client.start_query_execution(
        QueryString='select "date", "temperature" from "climate-data" order by "date" DESC',
        QueryExecutionContext={
            "Database": "ggpocdb",
            "Catalog": "awsdatacatalog"
        },
        ResultConfiguration={
            'OutputLocation': 's3://greengrass-poc-buck/athena-query/lambda/',
        },
        WorkGroup='primary'
    )
    return response


def query_result(client, response):
    response1 = client.get_query_execution(
        QueryExecutionId=response['QueryExecutionId'],
    )
    while (response1['QueryExecution']['Status']['State'] == 'QUEUED') or (response1['QueryExecution']['Status']['State'] == 'RUNNING'):
        response1 = client.get_query_execution(
            QueryExecutionId=response['QueryExecutionId'],
        )
    if response1['QueryExecution']['Status']['State'] == 'SUCCEEDED':
        os.environ["QueryExecutionId"] = response['QueryExecutionId']
        resp = result(client)
        return resp
    return response1


def result(client, token=None):
    if token:
        resp = client.get_query_results(
            QueryExecutionId=os.environ["QueryExecutionId"],
            NextToken=token,
            MaxResults=50
        )
        resp['NextToken'] = urllib.parse.quote(resp['NextToken'])
        return resp
    resp = client.get_query_results(
        QueryExecutionId=os.environ["QueryExecutionId"],
        MaxResults=50
    )
    resp['NextToken'] = urllib.parse.quote(resp['NextToken'])
    return resp


# response = query_exec(client)
# response1 = query_result(client, response)

def get(event, context):
    if event["queryStringParameters"]:
        data = event["queryStringParameters"]
        if "token" in data:
            try:
                print(data['token'])
                resp = result(client, data['token'])
                return {
                    'statusCode': 200,
                    'body': json.dumps(resp, default=str),
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
        data = {'message': "invalid query"}
        return {
            'statusCode': 400,
            'body': json.dumps(data, default=str),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
    response = query_exec(client)
    response1 = query_result(client, response)
    return {
        'statusCode': 200,
        'body': json.dumps(response1, default=str),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }
