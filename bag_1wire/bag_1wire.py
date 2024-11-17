#!/usr/bin/python3

import glob
import time
import paho.mqtt.client as mqtt
import json

import sys
sys.path.insert(0,"/root")
import BagMQTTClass

Broker = '10.2.90.35'
auth = {
    'username': 'mqttlogin',
    'password': 'mqttpass',
}

program_name = "OneWire"

all_mustbe_macs = ["28-61d883346461", "28-e52489346461", "28-a85489346461", "28-b86589346461", "28-d468cd346461", "28-a839c2346461", "28-a07fcf346461", "28-de7889346461", "28-146dd4457bf3", "28-0523d445b6e1", "28-58ddd4451e25", "28-967dcf346461", "28-d570cf346461", "28-4229d445e6db", "28-36d2d445af56", "28-de7889346461", "28-0bd9d4457e0e", "28-75ded445a8f4", "28-7ebdd4457338", "28-1534d4450a99", "28-1951d4453b78", "28-7a4ad445abf1", "28-1c29d4457ab9", "28-780fd4453c40", "28-17a8d44578d4", "28-2d29d445352e", "28-43a4d4450b15", "28-0851d445c4ad", "28-0337d445a56d", "28-6635d44563c1"]

# print (all_mustbe_macs)

CONNECT_TO_MQTT = False
PUB_MQTT_MQSSAGES = True
DEBUG_PROTOCOL = False
DEBUG_MQTT = False
DEBUG_PRINT = True
    
DEBUG = False

def tologread(msg):
    # call(["logger", "-t", program_name, msg])
    if DEBUG_PRINT:
        print(msg)


my_file = open("/root/device_id")
device_id = my_file.read()
my_file.close()

mqtt_credential_file_path = "/root/mqtt_credentials.json"
my_file = open(mqtt_credential_file_path)
my_string = my_file.read()
my_file.close()
mqtt_credentials_from_file_dict = json.loads(my_string)

MQTT_client_id_subscriber = device_id + '_bsr'







pub_topic = 'Onewire/temperature'

base_dir = '/sys/bus/w1/devices/'


dict_sample = {}


def get_subdirectories(directory):
    return [name for name in glob.glob(directory + '/*/')]

def make_mac_list():
    all_subdirs = get_subdirectories(base_dir)

    all_macs_list = []
    all_macs_list.clear()

    for val in all_subdirs:
        if "28-" in val:
            id = val[20:][:15]
            all_macs_list.append(id)
    # print("------------------------- all macs type list:")
    # print (all_macs_list)
    # print("-------------------------")
    return (all_macs_list)

    # device_folder = glob.glob(base_dir + '28-*')[0]
    # device_file = device_folder + '/w1_slave'


def read_temp(device_file):
    valid = False
    temp = 0
    with open(device_file, 'r') as f:
        for line in f:
            if line.strip()[-3:] == 'YES':
                valid = True
            temp_pos = line.find(' t=')
            if temp_pos != -1:
                temp = float(line[temp_pos + 3:]) / 1000.0

    if valid:
        return temp
    else:
        return None





def sendmqttconfigobject(mac):
    mac_safety = mac[3:]

    device_dict = {"identifiers": "mqtt_1wire", "mf": "Linux Python", "mdl": "bag_1wire.py", "sw": "1.0", "name": "OneWire"}
    T1_dict = []

    T1_dict = {
        "device": device_dict,
        "object_id": "mqtt_1wire_" + str(mac_safety),
        "unique_id": "mqtt_1wire_" + str(mac_safety),
        "name": mac_safety,
        "icon": "mdi:thermometer",
        "unit_of_measurement":"°C",
        "state_topic": MQTTtopic_header + str(mac) + "/state",
        'availability_mode': "all",
        "availability": [{"topic": "OneWire/temp/", "payload_available": "Online", "payload_not_available": "Offline"}, {"topic": "OneWire/temp/" + mac + "/status", "payload_available": "Online", "payload_not_available": "Offline"}]
    }
    if (PUB_MQTT_MQSSAGES): LocalBrocker.bag_pub("homeassistant/sensor/onewire/mac_" + mac_safety + "/config", json.dumps(T1_dict), retain = True, use_topic_header = False)
    time.sleep(0.2)



class LocalBrocker_on_message(BagMQTTClass.BagMQTTClass):
    def on_message(self, mqttc, obj, msg):
        if DEBUG:
            tologread("Recieved msg: {}, topic={}, brocker={}".format(str(msg.payload), msg.topic, self.BRname))

MQTTtopic_header = program_name + "/temp/" 
subscribe_to_topics = [(MQTTtopic_header + "command/#", 0)]
LWT_topic = MQTTtopic_header

LocalBrocker = LocalBrocker_on_message(client_id=program_name)
mqtt_cred_name="localnet"
if mqtt_cred_name not in mqtt_credentials_from_file_dict:
    tologread("Error: Credential for '" + mqtt_cred_name + "' does not exist in the file '" + mqtt_credential_file_path + "'")
    # when_exit()


LocalBrocker.setPlaces(
    name=mqtt_cred_name,
    host=mqtt_credentials_from_file_dict.get(mqtt_cred_name).get("host"),
    port=int(mqtt_credentials_from_file_dict.get(mqtt_cred_name).get("port")),
    user=mqtt_credentials_from_file_dict.get(mqtt_cred_name).get("user"),
    password=mqtt_credentials_from_file_dict.get(mqtt_cred_name).get("password"),
    topic_header=MQTTtopic_header,
    subscribe_to_topics = subscribe_to_topics,
    LWT_topic = LWT_topic,
    DEBUG=DEBUG)

LocalBrocker.BRinfo()
LocalBrocker.bag_will_set(MQTTtopic_header)
LocalBrocker.run2()


# print (all_mustbe_macs)

print("spleep 10 sec")
time.sleep(10)

for mac in all_mustbe_macs:
    # print("MAC=" + mac)
    sendmqttconfigobject(mac)


def check_all():
    all_macs_list2 = make_mac_list()
    # print ("-------------all_macs_list2 start")
    # print (all_macs_list2)
    # print ("-------------all_macs_list2 end")

    for mac in all_macs_list2:
        device_file = base_dir + mac + '/w1_slave'
        temp = read_temp(device_file)
        if temp is not None:
            dict_sample[mac] = temp
            LocalBrocker.bag_pub(str(mac) + "/state", temp)
            print ("111: " + mac + ": " + str(temp))
            LocalBrocker.bag_pub(str(mac) + "/status", "Online")
        else:
            LocalBrocker.bag_pub(str(mac) + "/status", "Offline")
        # break

    dict_all_status = {}
    for mac_from_all in all_mustbe_macs:
        # for mac_from_detected in all_macs_list2:
        if mac_from_all in all_macs_list2:
            dict_all_status[mac_from_all] = True
            # LocalBrocker.bag_pub(str(mac_from_all) + "/status", "Online")
        else:
            dict_all_status[mac_from_all] = False
            # LocalBrocker.bag_pub(str(mac_from_all) + "/status", "Offline")

    # print (type(dict_all_status))
    # print (dict_all_status)
    for mac_from_all, status in dict_all_status.items():
        if mac_from_all not in all_macs_list2:
            LocalBrocker.bag_pub(str(mac_from_all) + "/status", "Offline")


    # print ("------dict_all_status start------")
    # print (dict_all_status)
    # print ("------dict_all_status end------")







nnn = 30
while True:
    check_all()
    print ("Pause " + str(nnn) + " sec...")

    time.sleep(nnn)