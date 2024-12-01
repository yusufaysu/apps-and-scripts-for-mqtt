import customtkinter as ctk
import paho.mqtt.client as mqtt
import json
import time
from pygame import mixer
import os
import sys
import re
import csv

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def put_csv_to_arr(csvFilePath):
    data = []
    try:
        with open(csvFilePath, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = [row for row in reader]
    except FileNotFoundError:
        print(f"Dosya '{csvFilePath}' bulunamadı.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    
    return data

def isInCsv(seri_no):
    data = put_csv_to_arr(resource_path("assets/etap_2.csv"))
    for row in data:
        if row[2] == seri_no:
            return row[0], row[1]
    
    return (None, None)

def get_module_name(payload):
    try:
        # 'moduleName' anahtarını bul
        start_index = payload.find('"moduleName":')
        if start_index == -1:
            return None  # Anahtar bulunamazsa None döner

        # Anahtarın değerinin başladığı yeri bul
        start_index += len('"moduleName":')
        end_index = payload.find(',', start_index)  # Sonraki virgülü bul

        if end_index == -1:  # Eğer sonlandırıcı yoksa, '}' bul
            end_index = payload.find('}', start_index)

        if end_index == -1:  # Eğer hala bulunamıyorsa None döner
            return None

        # Değerin başlangıç ve bitişini kesip döndür
        module_name_value = payload[start_index:end_index].strip().strip('"')
        return module_name_value

    except Exception as e:
        print(f"Hata: {e}")
        return None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
mixer.init()
mixer.music.load(resource_path('assets/alarm.mp3'))
retain_topics = []

class App(ctk.CTk):
    def __init__(self, mqtt_clients):
        super().__init__()
        self.title("iCe Duyuru Paneli")
        self.iconbitmap(resource_path('assets/favicon.ico'))
        self.mqtt_clients = mqtt_clients
        self.setup_ui()

    def setup_ui(self):
        window_width, window_height = 1000, 650
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width - window_width) // 2, (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        frame = ctk.CTkFrame(master=self)
        frame.pack(pady=0, padx=0, fill="both", expand=True)

        # Create status lights for each client
        self.status_light_1 = ctk.CTkLabel(master=frame, width=2, height=20, corner_radius=10)
        self.status_light_1.place(x=20, y=25)

        self.status_light_2 = ctk.CTkLabel(master=frame, width=2, height=20, corner_radius=10)
        self.status_light_2.place(x=20, y=65)  # Adjusted position for second status light

        label = ctk.CTkLabel(master=frame, text="iCe Duyuru Paneli.", font=("Roboto Mono", 24))
        label.pack(pady=12, padx=10)

        self.entryBlok = ctk.CTkEntry(master=frame, placeholder_text="Lisans", font=("Roboto Mono", 24), width=300)
        self.entryBlok.pack(pady=12, padx=10)

        mesaj = ctk.CTkLabel(master=frame, text="Mesaj", font=("Roboto Mono", 24))
        mesaj.pack(pady=12, padx=10)

        self.entryMessage = ctk.CTkTextbox(master=frame, font=("Roboto Mono", 20), width=500, height=200)
        self.entryMessage.pack(pady=12, padx=10)

        self.checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(master=frame, text="Toplu mesaj", variable=self.checkbox_var)
        checkbox.pack(pady=12, padx=10)

        #sendButton = ctk.CTkButton(master=frame, text="Gönder", command=self.sendMsg) # mesaj gönderme olayı iptal edildi
        sendButton = ctk.CTkButton(master=frame, text="Gönder")
        sendButton.pack(pady=12, padx=10)

        log_frame = ctk.CTkFrame(master=frame)
        log_frame.pack(pady=12, padx=10, fill="both", expand=True)

        self.log_text = ctk.CTkTextbox(master=log_frame, font=("Roboto Mono", 12), wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

    def showLog(self, log_message, color):
        log_message_with_time = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {log_message}"

        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_message_with_time + "\n", color)
        self.log_text.configure(state="disabled")

        self.log_text.see("end")
        self.log_text.tag_config(color, foreground=color)

    #Kullanılmıyor iptal edildi
    def sendMsg(self):
        global retain_topics
        lisans = self.entryBlok.get()
        mesaj = self.entryMessage.get("1.0", "end-1c")

        if self.checkbox_var.get():
            if mesaj == "":
                self.showLog("Boş mesaj gönderilemez", "orange")
            else:
                self.showLog(f"DİKKAT! Tüm dairelere mesaj gönderiliyor.", "blue")
                for topic in retain_topics:
                    for client in self.mqtt_clients:
                        client.publish(f"/{topic}/devListener", f"""{{"com":"message", "text":"{mesaj}"}}""")
                self.showLog(f"DİKKAT! Tüm dairelere mesaj gönderildi.", "blue")
        else:
            if lisans == "" or mesaj == "":
                self.showLog("Boş bir kutu bırakmayınız", "orange")
            elif lisans.startswith("02.01.") == 0 or len(lisans) != 19:
                self.showLog("Yanlış lisans tipi", "orange")
            else:
                for client in self.mqtt_clients:
                    client.publish(f"/{lisans}/devListener", f"""{{"com":"message", "text":"{mesaj}"}}""")
                self.showLog(f"'{lisans}' lisanslı daireye '{mesaj}' mesajını gönderdiniz.", "blue")

    def alarmWindow(self, blok_no, daire_no, ircom):
        try:
            alarmWindow = NewWindow(blok_no, daire_no, ircom)
            alarmWindow.mainloop()
        except:
            pass

    def toggle_status_light(self, connection_status, client_id=0):
        color = "green" if connection_status == 0 else "red"
        status_text = "Online" if connection_status == 0 else "Offline"
        
        # Update the correct status light based on client_id
        if client_id == 1:
            self.status_light_1.configure(fg_color=color)
            self.status_light_1.configure(text=f"{status_text} - Client 1")
        elif client_id == 2:
            self.status_light_2.configure(fg_color=color)
            self.status_light_2.configure(text=f"{status_text} - Client 2")

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

    def setup_ui(self):
        label1 = ctk.CTkLabel(self, text=f"!!!{self.ircom} alarmı!!!", font=("Arial", 16), text_color="red")
        label1.pack(pady=10)

        label2 = ctk.CTkLabel(self, text=f"Blok No: {self.blok_no}\nDaire No: {self.daire_no}", font=("Arial", 16))
        label2.pack(pady=50)

        close_button = ctk.CTkButton(self, text="Kapat", command=self.close_window)
        close_button.pack()

    def close_window(self):
        self.destroy()

class Client:
    def __init__(self, app, broker, port, username=None, password=None, client_id=0):
        self.broker = broker
        self.port = port
        self.app = app
        self.client_id = client_id  # Yeni eklenen client ID
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc, properties):
        self.app.showLog(f"{self.broker} bağlantısı {rc}.", "green" if rc == 0 else "red")
        if self.client_id == 1:
            client.subscribe("#")
        if self.client_id == 2:
            client.subscribe("notification/#")
        self.app.toggle_status_light(rc, self.client_id)  # ID'yi kullanarak çağırın

    def on_disconnect(self, client, userdata, flags, rc, properties):
        if rc != 0:
            self.app.showLog(f"{self.broker} bağlantısı kesildi.", "red")
            self.app.toggle_status_light(1, self.client_id)  # ID'yi kullanarak çağırın

    def connect(self):
        try:
            return self.client.connect(self.broker, self.port, 10)
        except Exception as e:
            self.app.showLog(f"{self.broker} bağlantı hatası: {e}", "red")
            return 1

    def on_message(self, client, userdata, message):
        if self.client_id == 1:
            try:
                global retain_topics
                topic = message.topic
                payload = message.payload.decode("utf-8")
                topic_arr = topic.split('/')
                lisans = topic_arr[1]
                channel = topic_arr[2]

                if topic.startswith("/02.01.") and topic.endswith("/devWill"):
                    if topic not in retain_topics:
                        retain_topics.append(lisans)

                parsed_json = json.loads(payload)
                if channel == "devSender":
                    try:
                        blok_no = parsed_json["durum"]["counter"]
                        daire_no = parsed_json["durum"]["temp"]
                        ircom = parsed_json["durum"]["ircom"]
                        irval = parsed_json["durum"]["irval"]
                        if irval == "alarm" and lisans.startswith("02.01"):
                            self.app.showLog(f"|server id {self.client_id}| blok -> {blok_no} daire -> {daire_no} alarm -> {ircom} alarmı", "red")
                            self.app.alarmWindow(blok_no, daire_no, ircom)
                    except Exception:
                        pass
                #acil durum butonu iptal edildi
                #elif channel == "devSender":
                #    try:
                #        sen_com = parsed_json["com"]
                #        sen_no = parsed_json["no"]
                #        if sen_com == "sen" and sen_no == "99":
                #            self.app.showLog(f"{lisans} lisanslı dairede acil durum var!!!", "red")
                #            mixer.music.play()
                #    except Exception:
                #        pass
            except Exception as e:
                print(f"|Client 1| Mesaj işlenirken hata: {e}")
        if self.client_id == 2:
            try:
                topic = message.topic
                payload = message.payload.decode("utf-8")
                topic_arr = topic.split('/')
                seri_no = topic_arr[1]
                blok_daire_no = isInCsv(seri_no)
                
                if blok_daire_no is not None and blok_daire_no[0] is not None and blok_daire_no[1] is not None:
                    self.app.showLog(f"|server id {self.client_id}| Blok -> {blok_daire_no[0]} Daire -> {blok_daire_no[1]} Alarm -> {get_module_name(payload)}", "red")
                    self.app.alarmWindow(blok_daire_no[0], blok_daire_no[1], get_module_name(payload))
                else:
                    print(f"Seri numarası '{seri_no}' CSV dosyasında bulunamadı veya geçersiz.")
                    
            except Exception as e:
                print(f"|Client 2| Mesaj işlenirken hata: {e}")

    def start(self):
        self.client.loop_start()

    def publish(self, topic, message):
        self.client.publish(topic, message)

if __name__ == "__main__":
    app = App(mqtt_clients=[])

    client1 = Client(app, broker="icemqtt.com.tr", port=1883, client_id=1)
    client2 = Client(app, broker="www.icesmarthome.com", port=1883, username="testuser", password="tim21duncan", client_id=2)
    
    app.mqtt_clients.extend([client1, client2])

    for client in app.mqtt_clients:
        connection_status = client.connect()
        client.start()
        app.toggle_status_light(connection_status, client.client_id)  # ID'yi kullanarak çağırın

    app.mainloop()
