import os
import paho.mqtt.client as mqtt
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()
load_dotenv(env_file_path)

# MQTT sunucusuna bağlanma işlevi
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test/topic")  # İzlemek istediğiniz konu

# Mesaj alındığında çağrılan işlev
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# MQTT istemci oluşturma
client = mqtt.Client()
client.username_pw_set(username="ice", password="123")  # Kullanıcı adı ve şifre ayarı
client.on_connect = on_connect
client.on_message = on_message

# MQTT sunucusuna bağlanma
client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")), 60)  # MQTT sunucusunun adresi ve portu

# MQTT döngüsünü başlatma
client.loop_forever()
