import os
import paho.mqtt.client as mqtt
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()
load_dotenv(env_file_path)

mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = int(os.getenv("MQTT_PORT"))
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port)

print("\033[1;31mmesaj gönderildi\033[0m")

client.publish("/02.01.+/devListener", """{"com":"message","text":"sa"}""")
#client.publish("/02.01.6579C727.1111/devSender", """{"com":"event","id":7,"durum":{"stat":false,"status":4,"color":7,"ircom":"Su","irval":"alarm","counter":11,"temp":3,"act":true}}""")
#client.publish("/02.01.650099B3.516D/devSender", """{"com":"event","id":7,"durum":{"stat":true,"status":4,"color":7,"ircom":"Water","irval":"alarm","act":true}}""")
client.disconnect()


#/02.01.650099B3.516D/devListener Data: {"com":"token","fcm":"ezW4BPvxTzG3NEsdoNEaa9:APA91bEXGLcfWf6S4Un4fpsbyJJ1mUBmGZk-zpPSge7v9qptqAeaXaNyVL7DpKNx-G2NoEP6cMGDPiU_uqph-BBqJ4-F0uSOmZSRk_wqXcYGgZ2kmp7pUP67gnCHzHNnnfA7XTwvpwIB","key":"c4fdce825d95cdfb", "user":"5358904619"}
#/02.01.650099B3.516D/devListener Data: {"com":"auth","key":"c4fdce825d95cdfb", "user":"5358904619"}

#/02.01.650099B3.516D/devServer Data: {"com":"auth","key":"c4fdce825d95cdfb", "user":"5358904619","stat":true, "admin":true}
#topic: /02.01.650099B3.516D/devSender Data: {"com":"event","id":7,"durum":{"stat":true,"status":4,"color":7,"ircom":"Water","irval":"alarm","act":true}}
