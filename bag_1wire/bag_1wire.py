#!/usr/bin/python3

import glob
import time
import paho.mqtt.client as mqtt
import json

import sys
sys.path.insert(0,"/root")
import BagMQTTClass

loop_time = 30 # Через сколько секунд перечитывать температуру и посылать по MQTT. Чем ниже - тем больже значений сохранится в базе данных принимающей стороны

Broker = '10.5.10.3'
auth = {
    'username': 'mqttlogin',
    'password': 'mqttpass',
}

program_name = "OneWire"

pub_topic = 'Onewire/temperature'

base_dir = '/1wire/'

all_mustbe_macs = { # Нужно составить список МАС-адресов всех датчиков и пронумеровать их (наклеить на них маркировку 1, 2 и т.д.) и внести в этот словарь. 1-30 в данном случае - это проектные номера (номера, которые указаны в проектной документации)
    1: "28-61d883346461", 
    2: "28-e52489346461", 
    3: "28-a85489346461", 
    4: "28-b86589346461", 
    5: "28-d468cd346461", 
    6: "28-a839c2346461", 
    7: "28-a07fcf346461", 
    8: "28-de7889346461", 
    9: "28-146dd4457bf3", 
    10: "28-0523d445b6e1", 
    11: "28-58ddd4451e25", 
    12: "28-967dcf346461", 
    13: "28-d570cf346461", 
    14: "28-4229d445e6db", 
    15: "28-36d2d445af56", 
    # 16: "28-de7889346461", 
    17: "28-0bd9d4457e0e", 
    18: "28-75ded445a8f4", 
    19: "28-7ebdd4457338", 
    20: "28-1534d4450a99", 
    21: "28-1951d4453b78", 
    22: "28-7a4ad445abf1", 
    23: "28-1c29d4457ab9", 
    24: "28-780fd4453c40", 
    25: "28-17a8d44578d4", 
    26: "28-2d29d445352e", 
    27: "28-43a4d4450b15", 
    28: "28-0851d445c4ad", 
    29: "28-0337d445a56d", 
    30: "28-6635d44563c1"
}

dict_all_mustbe_macs = {}

for num, mac in all_mustbe_macs.items(): # Составляем словарь типа {1: {'mac1': '28-61d883346461', 'mac2': '61d883346461', 'inverted_mac1': '61643483d861', 'inverted_mac2': '28.61643483d861'}, 2: ...
    mac1 = mac.lower()
    mac2 = mac1[3:]
    
    
    m1 = mac1[13:]
    m2 = mac1[11:][:2]
    m3 = mac1[9:][:2]
    m4 = mac1[7:][:2]
    m5 = mac1[5:][:2]
    m6 = mac1[3:][:2]
    inverted_mac1 = (m1 + m2 + m3 + m4 + m5 + m6)
    inverted_mac2 = "28." + inverted_mac1
    
    # print(str(num) + ": " + mac1 + ": " + mac2 + ": " + inverted_mac1)
    dict_all_mustbe_macs[num] = {"mac1": mac1, "mac2": mac2, "inverted_mac1": inverted_mac1, "inverted_mac2": inverted_mac2}
    
# print (dict_all_mustbe_macs) # Здесь получится такое: {1: {'mac1': '28-61d883346461', 'mac2': '61d883346461', 'inverted_mac1': '61643483d861', 'inverted_mac2': '28.61643483d861'}, 2: {'mac1': '28-e52489346461', 'mac2': 'e52489346461', 'inverted_mac1': '6164348924e5', 'inverted_mac2': '28.6164348924e5'}, 3: {'mac1': '28-a85489346461', 'mac2': 'a85489346461', 'inverted_mac1': '6164348954a8', 'inverted_mac2': '28.6164348954a8'}, 4: {'mac1': '28-b86589346461', 'mac2': 'b86589346461', 'inverted_mac1': '6164348965b8', 'inverted_mac2': '28.6164348965b8'}, 5: {'mac1': '28-d468cd346461', 'mac2': 'd468cd346461', 'inverted_mac1': '616434cd68d4', 'inverted_mac2': '28.616434cd68d4'}, 6: {'mac1': '28-a839c2346461', 'mac2': 'a839c2346461', 'inverted_mac1': '616434c239a8', 'inverted_mac2': '28.616434c239a8'}, 7: {'mac1': '28-a07fcf346461', 'mac2': 'a07fcf346461', 'inverted_mac1': '616434cf7fa0', 'inverted_mac2': '28.616434cf7fa0'}, 8: {'mac1': '28-de7889346461', 'mac2': 'de7889346461', 'inverted_mac1': '6164348978de', 'inverted_mac2': '28.6164348978de'}, 9: {'mac1': '28-146dd4457bf3', 'mac2': '146dd4457bf3', 'inverted_mac1': 'f37b45d46d14', 'inverted_mac2': '28.f37b45d46d14'}, 10: {'mac1': '28-0523d445b6e1', 'mac2': '0523d445b6e1', 'inverted_mac1': 'e1b645d42305', 'inverted_mac2': '28.e1b645d42305'}, 11: {'mac1': '28-58ddd4451e25', 'mac2': '58ddd4451e25', 'inverted_mac1': '251e45d4dd58', 'inverted_mac2': '28.251e45d4dd58'}, 12: {'mac1': '28-967dcf346461', 'mac2': '967dcf346461', 'inverted_mac1': '616434cf7d96', 'inverted_mac2': '28.616434cf7d96'}, 13: {'mac1': '28-d570cf346461', 'mac2': 'd570cf346461', 'inver...





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








dict_sample = {}


def get_subdirectories(directory):
    return [name for name in glob.glob(directory + '/*/')]

def scan_online_macs(): # Составить лист МАС адресов датчиков, которые сейчас онлайн (без "28-" и "28.")
    all_subdirs = get_subdirectories(base_dir)

    all_macs_list = []
    
    for subdir_val in all_subdirs: # Перебираем всё что в папке
        if "28." in subdir_val: # Если в названии папки или файла есть "28."
            mac = subdir_val[7:22].lower() # Вырезаем МАС-адрес из полного пути папки "/1wire/28.387345d4bd7e/"
            for num, values in dict_all_mustbe_macs.items():
                if mac.lower() == values.get("inverted_mac2"): # Если итерируемый МАС-адрес из папки присутствует в общем списке МАС-адресов
                    all_macs_list.append(mac.lower()) # Добавляем этот МАС-адрес в отдельный массив, доступный только в этой функции
    return (all_macs_list)

def read_temp(device_file):
    with open(device_file, 'r') as f:
        data = f.read(6)
        return float(data)




def sendmqttconfigobject(num): # Посылаем MQTT-autodiscovery для указанного проектного номера датчика
    mac_safety = dict_all_mustbe_macs.get(num).get("mac2")

    device_dict = {"identifiers": "mqtt_1wire", "mf": "Linux Python", "mdl": "bag_1wire.py", "sw": "1.0", "name": "OneWire"}
    T1_dict = []

    T1_dict = {
        "device": device_dict,
        "object_id": "mqtt_1wire_" + str(mac_safety),
        "unique_id": "mqtt_1wire_" + str(mac_safety),
        "name": str(num) + ": " + mac_safety,
        "icon": "mdi:thermometer",
        "unit_of_measurement":"°C",
        "state_topic": MQTTtopic_header + mac_safety + "/state",
        'availability_mode': "all",
        "availability": [{"topic": "OneWire/temp/", "payload_available": "Online", "payload_not_available": "Offline"}, {"topic": "OneWire/temp/" + mac_safety + "/status", "payload_available": "Online", "payload_not_available": "Offline"}]
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



print("spleep 10 sec")
time.sleep(10)


for num, values in dict_all_mustbe_macs.items():  # Посылаем MQTT-autodiscovery для каждого датчика их общего списка МАС-адресов
    sendmqttconfigobject(num)


def check_all():
    owfs_online_macs = scan_online_macs() # В переменную помещаем список из найденных в папке МАС-адресов

    owfs_online_macs_and_temp_isset = [] # Список МАС адресов, у которых удалось прочитать температуру

    for owfs_mac in owfs_online_macs:
        device_file = base_dir + owfs_mac + '/temperature9' # temperature9 - быстрое чтение с низкой точностью. Это плохо работает с некоторыми совсем хреновыми датчиками
        temp = read_temp(device_file) # Читаем температуру
        if (temp > 80 or temp < -20): # У датчиков иногда хреновые значения (85, -2000). Ограничим диапазон
            continue

        for num, values in dict_all_mustbe_macs.items(): # Сопоставляем проектный номер датчика с тем что нашли в папке и получили нормальную температуру
            if owfs_mac == values.get("inverted_mac2"):
                current_num = num
        

        if temp is not None: # В системе owfs temp никогда не бывает None
            LocalBrocker.bag_pub(dict_all_mustbe_macs.get(current_num).get("mac2") + "/status", "Online") # Посылаем что датчик онлайн
            LocalBrocker.bag_pub(dict_all_mustbe_macs.get(current_num).get("mac2") + "/state", temp)      # Посылаем значение температуры
            owfs_online_macs_and_temp_isset.append(current_num)
        else:
            LocalBrocker.bag_pub(dict_all_mustbe_macs.get(current_num).get("mac2") + "/status", "Offline") # Посылаем что датчик офлайн

    for num, values in dict_all_mustbe_macs.items():
        if num not in owfs_online_macs_and_temp_isset: # Если проектный номер датчика отсутствует в списке
            LocalBrocker.bag_pub(dict_all_mustbe_macs.get(num).get("mac2") + "/status", "Offline") # Посылаем что датчик онлайн


while True:
    check_all()
    # print ("Pause " + str(nnn) + " sec...")

    time.sleep(loop_time)
