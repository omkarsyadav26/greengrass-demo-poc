import paho.mqtt.client as mqtt
import sys
import json
import re
import time
import traceback
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import GetThingShadowRequest,UpdateThingShadowRequest
from dataStore import upload_data_to_s3
from stream import KinesisFireHose
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest
)

print("Program start................................................")
publishtopic = "ac1/status"
updatetopic = "updatetopic"

THRESHOLD = 25
TIMEOUT = 10
PREVIOUS_TEMP = 0
MANUAL_OVERRIDE = "Off"
AC_STATUS = "Off"
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

def sample_get_thing_shadow_request(thingName, shadowName):
    try:
        # set up IPC client to connect to the IPC server
        ipc_client = awsiot.greengrasscoreipc.connect()
                
        # create the GetThingShadow request
        get_thing_shadow_request = GetThingShadowRequest()
        get_thing_shadow_request.thing_name = thingName
        get_thing_shadow_request.shadow_name = shadowName
        
        # retrieve the GetThingShadow response after sending the request to the IPC server
        op = ipc_client.new_get_thing_shadow()
        op.activate(get_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)
        print("get thing result:-",result)
        return result.payload
        
    except Exception as e:
        # add error handling
        print(e)
    # except ResourceNotFoundError | UnauthorizedError | ServiceError

def sample_update_thing_shadow_request(thingName, shadowName, payload):
    try:
        # set up IPC client to connect to the IPC server
        ipc_client = awsiot.greengrasscoreipc.connect()
                
        # create the UpdateThingShadow request
        update_thing_shadow_request = UpdateThingShadowRequest()
        update_thing_shadow_request.thing_name = thingName
        update_thing_shadow_request.shadow_name = shadowName
        update_thing_shadow_request.payload = payload
        print("update thing shadow request:",update_thing_shadow_request)
        # retrieve the UpdateThingShadow response after sending the request to the IPC server
        op = ipc_client.new_update_thing_shadow()
        op.activate(update_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)
        print("update thing result:-",result)
        return result.payload
        
    except Exception as e:
        # add error handling
        print("update shadow error:",e)
    # except ConflictError | UnauthorizedError | ServiceError

def on_connect(client, userdata, flags, rc):
    print("connected with result code", str(rc))

    client.subscribe("Topic/acstatus")


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    response_from_kinesis=kinesis_helper.post(json.loads(msg.payload))
    temp = re.findall(r'\d+', str(msg.payload))
    res = list(map(int, temp))
    print("Kinesis response : "+ response_from_kinesis)
    print("The numbers list is : " + str(res))
    upload_data_to_s3()
    ac_control(res)

def ac_control(res):
    global PREVIOUS_TEMP
    global THRESHOLD, AC_STATUS, MANUAL_OVERRIDE
    currentstate = {"state":{"reported":{}}}
    if MANUAL_OVERRIDE == "Off":
        if (PREVIOUS_TEMP < THRESHOLD) and (res[7] > PREVIOUS_TEMP) and (res[7] > THRESHOLD):
            msg = 'Turn On AC because temparature went up above {}°C, previous temperature was {}°C and now it is {}°C'.format(
                THRESHOLD, PREVIOUS_TEMP, res[7])
            AC_STATUS = "On"
            currentstate['state']['reported']['AC'] = AC_STATUS
            currentstate['state']['reported']['threshold'] = THRESHOLD
            sample_update_thing_shadow_request('gpoc', 'ACStatus', bytes(json.dumps(currentstate), "utf-8"))
            publish_to_ipcmqtt(msg)
        elif (PREVIOUS_TEMP > THRESHOLD) and (res[7] < PREVIOUS_TEMP) and (res[7] < THRESHOLD):
            msg = 'Turn Off AC because temparature went down below {}°C, previous temperature was {}°C and now it is {}°C'.format(
                THRESHOLD, PREVIOUS_TEMP, res[7])
            AC_STATUS = "Off"
            currentstate['state']['reported']['AC'] = AC_STATUS
            currentstate['state']['reported']['threshold'] = THRESHOLD
            sample_update_thing_shadow_request('gpoc', 'ACStatus', bytes(json.dumps(currentstate), "utf-8"))
            publish_to_ipcmqtt(msg)
    sample_get_thing_shadow_request('gpoc', 'ACStatus')
    PREVIOUS_TEMP = res[7]

def publish_to_ipcmqtt(msg):
    '''below code is for publishing messages on mqtt'''
    message = {}
    message["output"] = msg
    msgstring = json.dumps(message)
    pubrequest = PublishToIoTCoreRequest()
    pubrequest.topic_name = publishtopic
    pubrequest.payload = bytes(msgstring, "utf-8")
    pubrequest.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(pubrequest)
    future = operation.get_response()
    future.result(TIMEOUT)


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        global THRESHOLD
        global MANUAL_OVERRIDE
        global AC_STATUS
        message = str(event.message.payload, "utf-8")
        a = json.loads(message)
        if "Threshold" in a:
            THRESHOLD = a["Threshold"]
        if "manualOverride" in a:
            MANUAL_OVERRIDE = a["manualOverride"]
        if "acStatus" in a:
            currentstate = {"state":{"reported":{}}}
            AC_STATUS = a["acStatus"]
            currentstate['state']['reported']['AC'] = AC_STATUS
            currentstate['state']['reported']['threshold'] = THRESHOLD
            sample_update_thing_shadow_request('gpoc', 'ACStatus', bytes(json.dumps(currentstate), "utf-8"))

    def on_stream_error(self, error: Exception) -> bool:
        return True

    def on_stream_closed(self) -> None:
        pass


subrequest = SubscribeToIoTCoreRequest()
subrequest.topic_name = updatetopic
subrequest.qos = qos
subhandler = StreamHandler()
suboperation = ipc_client.new_subscribe_to_iot_core(subhandler)
future = suboperation.activate(subrequest)
future.result(TIMEOUT)

client = mqtt.Client()
kinesis_helper=KinesisFireHose(StreamName="gpocKinesisStream") 
print(kinesis_helper.describe)
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)


client.loop_forever()