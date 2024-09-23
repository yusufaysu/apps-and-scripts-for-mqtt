import os
import paho.mqtt.client as mqtt
import json
import mysql.connector
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()
load_dotenv(env_file_path)

broker_address = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

client = mqtt.Client()
client.connect(broker_address, port, 60)

db = mysql.connector.connect(
    host="localhost",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="ice"
)

if db.is_connected():
    print("MySQL veritabanına bağlandı")

def addDb(lisans, ircom):
    try:
        cursor = db.cursor()
        tarih_saat = datetime.now()
        cursor.execute("INSERT INTO alarm (lisans, ircom, datetime) VALUES (%s, %s, %s)",
            (lisans, ircom, tarih_saat))
        cursor.execute("commit")
        print("Alarm oluşturuldu.")
    except Exception as e:
        print("Hata : ", e)


def on_message(client, userdata, message):
    topic       = message.topic
    payload     = message.payload
    topic_arr   = topic.split('/')
    lisans      = topic_arr[1]
    channel     = topic_arr[2]
    topic       = message.topic
    payload     = message.payload.decode("utf-8")

    try:
        parsed_json = json.loads(payload)
        com         = parsed_json.get('com')
        durum       = parsed_json.get('durum')
        
        if 'durum' in parsed_json and 'status' in parsed_json['durum']:
            status = parsed_json['durum']['status']
        else:
            status = None

        if 'durum' in parsed_json and 'irval' in parsed_json['durum']:
            irval = parsed_json['durum']['irval']
        else:
            irval = None

        if 'durum' in parsed_json and 'ircom' in parsed_json['durum']:
            ircom = parsed_json['durum']['ircom']
        else:
            ircom = None

    except json.JSONDecodeError:
        print("Invalid JSON.")

    #print(com, "-", status, "-", irval)
    if com == "event" and status == 4 and irval == "alarm":
        addDb(lisans, ircom)

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
