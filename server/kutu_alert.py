import os
import firebase_admin
import paho.mqtt.client as mqtt
import mysql.connector
import json
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()
print(env_file_path)
load_dotenv(env_file_path)

broker_address = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

db = mysql.connector.connect(
    host="localhost",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="ice"
)

if db.is_connected():
    print("MySQL veritabanına bağlandı")

client = mqtt.Client()
client.connect(broker_address, port, 60)

# Firebase Admin info
cred = credentials.Certificate("fcmserviceaccount.json")
firebase_admin.initialize_app(cred)

def send_notification(lisans, title, message):
    #full hepsine
    if lisans is None:
        sql = "SELECT kutu_fcm FROM kutu_alert"

        cursor = db.cursor()
        cursor.execute(sql)

        fcm_keys = cursor.fetchall()

        for fcm in fcm_keys:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                token=fcm[0],
            )
            print("ehe")
            response = messaging.send(message)
            print("aha")
        cursor.close()
    #lisansı aynı olanlar
    else:
        cursor = db.cursor()

        sql_query = f"SELECT kutu_fcm FROM kutu_alert WHERE kutu_lisans = '{lisans}'"
        cursor.execute(sql_query)

        fcm_keys = cursor.fetchall()

        for fcm in fcm_keys:
            message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            token=fcm[0],
        )
            response = messaging.send(message)
        cursor.close()

def isAdmin(lisans, key):
    try:
        cursor0 = db.cursor()
        adm = 0
        cursor0.execute("SELECT * FROM kutu_alert WHERE kutu_lisans=%s AND kutu_key=%s AND admin=1", (lisans, key))
        cursor0.fetchall()
        row_count = cursor0.rowcount
        if row_count<1:
            adm=1
        cursor0.close();
        print(f"ADM ({adm})")
        return adm
    except Exception as e:
        print("Hata 1 :", e)
        return 0

def checkLisansAndSet(lisans, fcm, key, user):

    try:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM kutu_alert WHERE kutu_lisans=%s AND kutu_key=%s", (lisans, key))
        existing_record = cursor.fetchone()
    
        isadmin = isAdmin(lisans, key)
        print(isadmin)

        # if no lisans
        if existing_record is None:
            tarih_saat = datetime.now()
            cursor.execute("INSERT INTO kutu_alert (kutu_lisans, kutu_fcm, kutu_key, date, user, active, admin) VALUES (%s, %s, %s, %s, %s, 1, %s)",
                           (lisans, fcm, key, tarih_saat, user, isadmin))
            cursor.execute("commit")
            print("Yeni bir öğe oluşturuldu.")
            return 1

        elif existing_record[2] != fcm :
            #fcm farklı ise
            tarih_saat = datetime.now()
            cursor.execute("UPDATE kutu_alert SET kutu_fcm=%s, date=%s WHERE kutu_key=%s",
                           (fcm, tarih_saat, key ))
            cursor.execute("commit")
            print("Lisansın bilgileri güncellendi.")
            return 1
        else:
            #fcm ve key eşit ise
            tarih_saat = datetime.now()
            cursor.execute("UPDATE kutu_alert SET date=%s WHERE kutu_lisans=%s and kutu_key=%s",
                           (tarih_saat, lisans, key))
            cursor.execute("commit")
            print(f"Lisans zaten var ve fcm/key aynı. Date time güncellendi. ({tarih_saat})")
            return 1

    except Exception as e:
        print("Hata 2 :", e)
        return 0


def send_auth(topic, lisans, key, user):
    try:
        cursor1 = db.cursor()
        cursor1.execute("SELECT admin, active FROM kutu_alert WHERE kutu_lisans=%s AND kutu_key=%s AND user=%s", (lisans, key, user))
        rec = cursor1.fetchone()
        print("Auth a cevap veriliyor")
        if rec is None:
            msg = '{"com":"auth","key":"'+key+'", "user":"'+user+'","stat":false, "admin":false}'
            print(msg)
            client.publish(topic, msg)
        else:
            aadm = "false"
            aact = "false"
            print(rec[0], rec[1])
            if rec[0]==1:
                aadm="true"
            if rec[1]==1:
                aact="true"
            msg = '{"com":"auth","key":"'+key+'", "user":"'+user+'","stat":'+aact+', "admin":'+aadm+'}'
            print(msg)
            client.publish(topic, msg)
        print("Cursor kapandı")
        cursor1.close()
    except Exception as e:
        print("Auth Error :", e)
        return 0        

def parseAndRun(topic, payload):
    topic_arr = topic.split('/')
    lisans = topic_arr[1]
    channel = topic_arr[2]
    send_topic = "/" + lisans + "/devServer"

    #print(topic)
    #print(payload)

    try:
        parsed_json = json.loads(payload)
        com     = parsed_json.get('com')
        fcm     = parsed_json.get('fcm')
        key     = parsed_json.get('key')
        user    = parsed_json.get('user')
        mes     = parsed_json.get('mes')
        head    = parsed_json.get('head')

        if not topic.endswith("/devServer") and com=='auth':
            send_auth(send_topic,lisans,key,user)


        if 'durum' in parsed_json and 'color' in parsed_json['durum']:
            color = parsed_json['durum']['color']
        else:
            color = None
        if 'durum' in parsed_json and 'ircom' in parsed_json['durum']:
            ircom = parsed_json['durum']['ircom']
        else:
            color = None
        if 'durum' in parsed_json and 'irval' in parsed_json['durum']:
            irval = parsed_json['durum']['irval'].upper()
        else:
            color = None

        if not topic.endswith("/devServer") and fcm and key:
            if (checkLisansAndSet(lisans, fcm, key, user)):
                client.publish(send_topic, payload)
                print(f"gönderildi topic -> {send_topic} payload -> {payload}")
        
        if topic_arr[1] == "$share" and topic_arr[2] == "adv":
            send_notification(None, head, mes)
        elif topic_arr[1] == "$share" and topic_arr[3] == "ice":
            send_notification(topic_arr[2], head, mes)
        if topic_arr[2] == "devSender" and color and ircom:
            temp = "Sisteminizde "+ircom+" alarmı oluştu. Lütfen program aracılığı ile kontrol ediniz."
            send_notification(topic_arr[1], irval, temp)

    except json.JSONDecodeError:
        print("JSON verileri geçerli değil.")


def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    parseAndRun(topic, payload)

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
    if db.is_connected():
        db.close()