import os
import paho.mqtt.client as mqtt

broker_address = "www.icesmarthome.com"
port = 1883
username = "testuser"
password = "tim21duncan"

# MQTT istemcisi oluştur
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Kullanıcı adı ve şifreyi ayarla
client.username_pw_set(username, password)

# Bağlantı fonksiyonu
def on_connect(client, userdata, flags, rc, properties):
    print(f"Bağlantı durumu: {rc}")
    # Abone ol
    client.subscribe("#")

# Mesaj alma fonksiyonu
def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    print(f"topic: {topic} Data: {payload}")

# Geri çağırma fonksiyonlarını ayarla
client.on_connect = on_connect
client.on_message = on_message

# Sunucuya bağlan
client.connect(broker_address, port, 60)

# Döngüyü başlat
client.loop_start()

try:
    while True:
        pass
except KeyboardInterrupt:
    # Ctrl+C ile çıkış
    client.disconnect()
    client.loop_stop()
