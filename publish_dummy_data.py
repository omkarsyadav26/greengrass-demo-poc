import paho.mqtt.client as mqtt
import random
import threading
import json
from datetime import datetime

# ====================================================
# MQTT Settings
MQTT_Broker = "test.mosquitto.org"
MQTT_Port = 1883
Keep_Alive_Interval = 45
MQTT_Topic_Temperature = "Topic/acstatus"

# ====================================================


def on_connect(client, userdata, rc):
    if rc != 0:
        pass
        print("Unable to connect to MQTT Broker...")
    else:
        print("Connected with MQTT Broker: " + str(MQTT_Broker))


def on_publish(client, userdata, mid):
    pass


def on_disconnect(client, userdata, rc):
    if rc != 0:
        pass


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))


def publish_To_Topic(topic, message):
    mqttc.publish(topic, message)
    print("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
    print("")


# ====================================================
# FAKE SENSOR
# Dummy code used as Fake Sensor to publish some random values
# to MQTT Broker

def publish_Fake_Sensor_Values_to_MQTT():
    threading.Timer(3.0, publish_Fake_Sensor_Values_to_MQTT).start()

    Temperature_Fake_Value = float("{0:.2f}".format(random.uniform(20, 30)))

    Temperature_Data = {}
    Temperature_Data['Sensor_ID'] = "Dummy-1"
    # yyyy-mm-dd HH:MM:SS
    Temperature_Data['Date'] = (
        datetime.today()).strftime("%Y-%m-%d %H:%M:%S")
    # datetime.today()).strftime("%d-%b-%Y %H:%M:%S:%f")
    Temperature_Data['Temperature'] = Temperature_Fake_Value
    temperature_json_data = json.dumps(Temperature_Data)

    print("Publishing fake Temperature Value: " +
          str(Temperature_Fake_Value) + "...")
    publish_To_Topic(MQTT_Topic_Temperature, temperature_json_data)


publish_Fake_Sensor_Values_to_MQTT()

# ====================================================
