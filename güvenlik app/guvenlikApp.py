import customtkinter as ctk
import paho.mqtt.client as mqtt
import json
import time
import threading
from pygame import mixer  # Load the popular external library
import os
import sys

#taken this function from: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2 # unutma :)
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

mixer.init()
mixer.music.load(resource_path('assets\\alarm.mp3'))

class App(ctk.CTk):
    def __init__(self, mqtt_client):
        super().__init__()
        self.title("iCe Duyuru Paneli")
        self.iconbitmap(resource_path('assets\\favicon.ico'))
        self.mqtt_client = mqtt_client  # Store the Client instance
        self.setup_ui()

    def setup_ui(self):
        # Pencere boyutu ve konumu
        window_width, window_height = 1000, 850
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width - window_width) // 2, (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Frame
        frame = ctk.CTkFrame(master=self)
        frame.pack(pady=0, padx=0, fill="both", expand=True)

        self.status_light = ctk.CTkLabel(master=frame, width=2, height=20, corner_radius=10)
        self.status_light.place(x=20, y=25)  # Yerleşimi ayarla

        label = ctk.CTkLabel(master=frame, text="iCe Duyuru Paneli.", font=("Roboto Mono", 24))
        label.pack(pady=12, padx=10)

        self.entryBlok = ctk.CTkEntry(master=frame, placeholder_text="Lisans", font=("Roboto Mono", 24), width=300)
        self.entryBlok.pack(pady=12, padx=10)

        mesaj = ctk.CTkLabel(master=frame, text="Mesaj", font=("Roboto Mono", 24))
        mesaj.pack(pady=12, padx=10)

        self.entryMessage = ctk.CTkTextbox(master=frame, font=("Roboto Mono", 20), width=500, height=200)
        self.entryMessage.pack(pady=12, padx=10)

        checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(master=frame, text="Toplu mesaj", variable=checkbox_var)
        checkbox.pack(pady=12, padx=10)

        sendButton = ctk.CTkButton(master=frame, text="Gönder", command=self.sendMsg)
        sendButton.pack(pady=12, padx=10)

        #self.bind("<Configure>", self.on_resize)  # Pencere boyutu değiştiğinde on_resize fonksiyonunu çağır

        # Log ekranı için frame
        log_frame = ctk.CTkFrame(master=frame)
        log_frame.pack(pady=12, padx=10, fill="both", expand=True)

        self.log_text = ctk.CTkTextbox(master=log_frame, font=("Roboto Mono", 12), wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

    def showLog(self, log_message, color):
        #current time i alip mesajin basina koy
        log_message_with_time = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {log_message}"

        # Log mesajını ekle
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_message_with_time + "\n", color)
        self.log_text.configure(state="disabled")

        # Otomatik olarak en altta göster
        self.log_text.see("end")

        self.log_text.tag_config(color, foreground=color)

    def sendMsg(self):
        lisans = self.entryBlok.get()
        mesaj = self.entryMessage.get("1.0", "end-1c")

        if lisans.startswith("02.01.") == 0 or len(lisans) != 19:
            self.showLog("Yanlış lisans tipi", "orange")

        elif lisans=="" or mesaj=="":
            self.showLog("Boş bir kutu bırakmayınız", "orange")
        
        else:
            self.mqtt_client.publish(f"/{lisans}/devListener", f"""{{"com":"message", "text":"{mesaj}"}}""")
            self.showLog(f"'{lisans}' lisanslı daireye '{mesaj}' mesajını gönderdiniz.", "blue")

    def alarmWindow(self, blok_no, daire_no, ircom):
        try:
            alarmWindow = NewWindow(blok_no, daire_no, ircom)
            alarmWindow.mainloop()
        except:
            pass

    def on_resize(self, event):
        x = self.winfo_width() - 100  # X konumunu güncelle
        y = 25  # Y konumunu sabit tut
        self.status_light.place(x=x, y=y)

    def toggle_status_light(self, connection_status):
        if connection_status == 0:
            self.status_light.configure(fg_color="green")
            self.status_light.configure(text="Online")
        else:
            self.status_light.configure(fg_color="red")
            self.status_light.configure(text="Offline")

class NewWindow(ctk.CTk):
    def __init__(self, blok_no, daire_no, ircom, master=None):
        super().__init__(master)
        self.title(f"Pencere - Blok {blok_no}, Daire {daire_no}")
        self.geometry("400x300")
        self.blok_no = blok_no
        self.daire_no = daire_no
        self.ircom = ircom
        self.setup_ui()

        self.alarm_playing = True

        self.protocol("WM_DELETE_WINDOW", self.close_window)
        mixer.music.play()

        #self.alarm_thread = threading.Thread(target=self.play_alarm)
        #self.alarm_thread.daemon = True  # Make the thread a daemon so it stops when the main program stops
        #self.alarm_thread.start()

    def setup_ui(self):
        # Blok numarasını ve daire numarasını ekrana yazdır
        label1 = ctk.CTkLabel(self, text=f"!!!{self.ircom} alarmı!!!", font=("Arial", 16), text_color="red")
        label1.pack(pady=10)

        label2 = ctk.CTkLabel(self, text=f"Blok No: {self.blok_no}\nDaire No: {self.daire_no}", font=("Arial", 16))
        label2.pack(pady=50)

        # Kapatma butonu
        close_button = ctk.CTkButton(self, text="Kapat", command=self.close_window)
        close_button.pack()

    def close_window(self):
        self.destroy()

class Client():
    def __init__(self, app, broker="icemqtt.com.tr", port=1883):
        self.broker = broker
        self.port = port
        self.app = app
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc, i):
        app.showLog("Server connection is "+str(rc) + ".", "green")
        client.subscribe("/+/devSender")
        self.app.toggle_status_light(0)

    def on_disconnect(self, client, userdata, flags, rc, i):
        if rc != 0:
            app.showLog("Server connection is lost.", "red")
            self.app.toggle_status_light(1)

    def connect(self):
        try:
            return (self.client.connect(self.broker, self.port, 60))
        except Exception as e:
            return (1)

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode("utf-8")
        topic_arr = topic.split('/')
        lisans = topic_arr[1]
        try:
            parsed_json= json.loads(payload)
            blok_no = parsed_json["durum"]["counter"]
            daire_no = parsed_json["durum"]["temp"]
            ircom = parsed_json["durum"]["ircom"]
            irval = parsed_json["durum"]["irval"]
            #alarm durumu
            if irval == "alarm" and lisans.startswith("02.01"):
                app.showLog(f"blok -> {blok_no} daire -> {daire_no} alarm -> {ircom} baskın alarmı", "red")
                app.alarmWindow(blok_no, daire_no, ircom)
        except Exception as e:
            pass

    def start(self):
        self.client.loop_start()

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)


if __name__ == "__main__":
    app = App(mqtt_client=None)  # Temporary None, to be updated later
    mqtt_client = Client(app)
    app.mqtt_client = mqtt_client  # Assign the MQTT client to the App
    connection_status = mqtt_client.connect()
    mqtt_client.start()
    app.toggle_status_light(connection_status)
    app.mainloop()