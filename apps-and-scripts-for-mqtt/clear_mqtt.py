import paho.mqtt.client as mqtt

# Broker bilgileri
broker_address = "localhost"  # Broker adresi
retain_topics = []

# Mesaj geldiğinde çalışacak fonksiyon
def on_message(client, userdata, message):
    topic = message.topic
    retain_topics.append(topic)

# MQTT client kurulum
client = mqtt.Client()
client.on_message = on_message

# Broker'a bağlanma
client.connect(broker_address)

# Tüm başlıkları dinle
client.subscribe("#")
client.loop_start()

# Bekle ki mesajlar toplansın
import time
time.sleep(5)

# Loop'u kapat
client.loop_stop()

# Tüm retain edilen başlıklara boş mesaj gönder
for topic in retain_topics:
    client.publish(topic, payload=None, retain=True)
