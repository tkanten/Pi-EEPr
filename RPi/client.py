from paho.mqtt import client as mqtt
from time import sleep
from Database import db, COLLECTIONS


class MqttClient:
    connected = False

    last_topic = ""
    last_message = ""

    def __init__(self, client_id, host=db["MQTT_HOST"],
                 port=db["MQTT_PORT"], username=db["MQTT_USERNAME"], password=db["MQTT_PASSWORD"]):
        # Create client object
        self.client = mqtt.Client(client_id=client_id, clean_session=True,
                                  userdata=None, protocol=mqtt.MQTTv311, transport="tcp")

        # asyncronus calls of each function
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe

        # Connect client
        self.client.connect(host, port=port, keepalive=60)
        self.client.username_pw_set(username=username, password=password)

        self.client.loop_start()

    def add_subscription(self, topic_to_add="#"):
        while (not self.connected):
            sleep(0.5)
        self.client.subscribe((topic_to_add, 0))

    def remove_subsription(self, topic_to_remove):
        self.client.unsubscribe(topic_to_remove)

    def publish(self, topic, message):
        while (not self.connected):
            sleep(0.5)
        self.client.publish(topic, message, qos=0)

    # General MQTT methods (to be changed and removed as needed)
    def on_connect(self, client, userdata, flags, rc):
        """when the device connects to the portal this function will run, alerting the user"""
        self.connected = True
        # print("Device connected with result code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        """when the device disconnects from the portal this function will run, alerting the user"""
        self.connected = False
        # print("Device disconnected with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        """when the device publishes to the portal this function will run, alerting the user"""
        # print("Device sent message")

    def on_message(self, client, userdata, message):
        """when the device recives a message from the portal this function will run, alerting the user"""
        # print("Received message:", str(message.payload),
        #       " \non topic:\n\t", str(message.topic))

        self.last_message = message.payload
        self.last_topic = message.topic

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """when the device subscribes to the portal this function will run, alerting the user"""
        # print("Client subscribed")

    def on_unsubscribe(self, client, userdata, mid):
        """when the device unsubscibes to the portal this function will run, alerting the user"""
        # print("Client Unsubscribed")
