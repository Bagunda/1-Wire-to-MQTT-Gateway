import paho.mqtt.client as mqtt
from subprocess import call

class BagMQTTClass(mqtt.Client):
    rc_txt = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised",
        7: "Connection refused - Unexpected disconnection",
        100: "Connection refused - other things"
    }

    def setPlaces(self, name, host, port, user, password, topic_header, subscribe_to_topics, LWT_topic, DEBUG):
        self.BRname = name
        self.BRhost = str(host)
        self.BRport = (port)
        self.BRuser = str(user)
        self.BRpassword = str(password)
        self.BRclient_id = str(self._client_id)
        self.BRtopic_header = str(topic_header)
        self.subscribe_to_topics = subscribe_to_topics
        self.LWT_topic = str(LWT_topic)
        self.DEBUG = DEBUG
        self.connected_flag = False


    def tologread(self, msg):
        # call(["logger", "-t", program_name, msg])
        # if DEBUG_PRINT:
            print(msg)
            
    def BRinfo(self):
        self.tologread ("Connection data: {} ({}:{}), u={}, pass={}, client_id={}, topic_header={}".format(self.BRname, self.BRhost, self.BRport, self.BRuser, self.BRpassword, self.BRclient_id, self.BRtopic_header))
        pass

    def on_disconnect(self, mqttc, userdata, rc):
        if rc != 0:
            self.connected_flag = False
            print ("rc====" + str(rc))
            if (rc in self.rc_text):
                self.tologread("Unexpected disconnection. Brocker=" + self.BRname + ", rc: " + str(rc) + " (" + self.rc_txt[rc] + ")")
            else:
                self.tologread("Unexpected disconnection. Brocker=" + self.BRname + ", rc: " + str(rc) + " (etogo id rc netu v rc_txt)")
            # tozabbix("mqtt_disconnect", "1")

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0: # 0 - Connection successful
            self.connected_flag=True

            for topic in self.subscribe_to_topics:
                print (topic)
                res = self.subscribe(topic)

                if res[0] == mqtt.MQTT_ERR_SUCCESS:
                    self.tologread("Successfully subscribed to topic: " + topic[0])
                else:
                    self.tologread("Error! Client is not subscribed to topic " + topic)
                    # tozabbix("mqtt_disconnect", "1")
                    
            self.publish(self.LWT_topic, "Online", qos=0, retain=True)
        else:
            self.connected_flag = False
            # tozabbix("mqtt_disconnect", "1")
            self.tologread("Brocker=" + self.BRname + ", rc: " + str(rc) + " (" + self.rc_txt[rc] + ")")
            self.tologread("Unexpected disconnection (maybe)")

    def on_connect_fail(self, mqttc, obj):
        self.tologread("Connect failed")

    def on_message(self, mqttc, obj, msg):
        self.tologread("Etogo ne doljno byt")
        self.tologread(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def on_publish(self, mqttc, obj, mid):
        if self.DEBUG:
            self.tologread("Message is published success. mid="+str(mid))

    def bag_pub(self, topic, payload, retain=False, use_topic_header = True):
        if (self.connected_flag == True):
            if use_topic_header == True:
                topic2 = self.BRtopic_header + topic
            else:
                topic2 = topic
            
            (rc, mid) = self.publish(topic2, payload, retain=retain)
            if self.DEBUG:
                self.tologread ("Try to sending mqtt: Brocker={}, mid={}, t={}, msg={}".format(self.BRname, str(mid), topic2, payload))
            if (rc != 0):
                self.connected_flag = False
                self.tologread("Error to send mqtt. rc=" + str(rc) + ". " + str(self.rc_txt[rc]) + ". mid=" + str(mid))
                # tozabbix("mqtt_pub_err", str(rc) + ": " + str(self.rc_txt[rc]))
            # else:
            #     self.tologread ("Send mqtt: {}, t={}, msg={}".format(self.BRname, topic2, payload))
        else:
            self.tologread ("Scipped trying send mqtt because connected_flag = False")

    def bag_pub_raw_topic(self, topic, payload, retain=False):
        if (self.connected_flag == True):

            (rc, mid) = self.publish(topic, payload, retain=retain)
            if self.DEBUG:
                self.tologread ("Try to sending mqtt: Brocker={}, mid={}, t={}, msg={}".format(self.BRname, str(mid), topic, payload))
            if (rc != 0):
                self.connected_flag = False
                self.tologread("Error to send mqtt. rc=" + str(rc) + ". " + str(self.rc_txt[rc]) + ". mid=" + str(mid))
        else:
            self.tologread ("Scipped trying send mqtt because connected_flag = False")
    
    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        if self.DEBUG:
            self.tologread("Successfully subscribed: Brocker=" + self.BRname + ", subscribed: mid=" + str(mid) + ", granted_qos=" + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        # print(string)
        # self.tologread("onlog: " + str(string))
        pass

    def bag_will_set(self, topic):
        self.will_set(self.LWT_topic, "Offline", qos=0, retain=True)
    
    def run2(self):
        self.will_set(self.LWT_topic, payload="Offline", qos=0, retain=True)

        self.username_pw_set(username=self.BRuser,password=self.BRpassword)

        try:
            self.connect(self.BRhost, self.BRport, 60)
        except Exception as err:
            # print (type(err))
            # print (err)
            # errno, error_string = err
            self.tologread("Error to connect mqtt. Info: {}. Broker={}".format(str(err), self.BRname))
            # tozabbix("mqtt_connect_error", 1)
        else:
            # tozabbix("mqtt_connect_error", "0")
            pass

        self.loop_start()

    def exit(self):
        if self.DEBUG:
            self.tologread("Paho mqtt is stoping...")
        self.bag_pub_raw_topic(self.LWT_topic, payload="Offline", retain=True)
        self.disconnect()
        self.loop_stop()
