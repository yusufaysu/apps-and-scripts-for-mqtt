import os
import paho.mqtt.client as mqtt

broker_address = "icemqtt.com.tr"
port = 1883

client = mqtt.Client(callback_api_version=2)
client.connect(broker_address, port, 60)

channels_list = []
i = 0

def on_message(client, userdata, message):
    global i
    topic = message.topic
    payload = message.payload.decode("utf-8")

    if topic.startswith("/02.01.") and topic.endswith("/devWill"):
        if topic not in channels_list:
            if topic not in channels_list:
                channels_list.append(topic)
                i += 1
                print(f"New channel added: {topic} - {i}")

client.on_message = on_message
client.subscribe("/#")
client.loop_start()

try:
    while True:
        pass
except KeyboardInterrupt:
    # Ctrl+C olayı
    client.disconnect()
    client.loop_stop()