#from https://youtu.be/xrYDlx8evR0?si=1rLx5PTNtdauOyt_
import signal
import time
import os
from dotenv import load_dotenv
import math
import json
import paho.mqtt.client as mqtt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# from https://blenderartists.org/t/invoke-function-before-closing-script-ctrl-c/1409269/2
default_handler = None
def handler(num, frame):    
    # Do something that cannot throw here (important)
    mqttc.loop_stop()
    driver.quit()

    return default_handler(num, frame) 

if __name__ == "__main__":
    default_handler = signal.getsignal(signal.SIGINT)

    # Assign the new handler
    signal.signal(signal.SIGINT, handler)

def on_connect(client, userdata, flags, reason_code, properties):
    # print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    return

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
load_dotenv()
path = os.environ
driver.get(path.get("TURBOLAB_URL"))
mqttTopic = path.get("BOX") + "/" + path.get("CUBE") + "/" + path.get("TRAYTYPE") + "/" + path.get("TRAYNAME") + "/reading"

def on_message(client, userdata, msg):
#    print(msg.topic+" "+str(msg.payload))
    return

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=path.get("MQTTCLIENTID"))
mqttc.username_pw_set(username=path.get("MQTTUSERNAME"),password=path.get("MQTTPASSWORD"))
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(path.get("MQTTSERVERIP"), 1883, 60)
mqttc.loop_start()
time.sleep(int(path.get("WEBLOAD_DELAY")))
status= {
    "power" : 0,
    "freq" : 0,
    "bearing" : 0,
    "current" : 0,
    "gauge1" : 0,
    "gauge2": 0,
    "watchdog": 0
}
runLoop = True
while runLoop:
    try:
        status["power"] = float(driver.find_element(By.ID,"5v").text)
        status["freq"] = float(driver.find_element(By.ID,"2v").text)
        status["bearing"] = float(driver.find_element(By.ID,"20v").text)
        status["current"] = float(driver.find_element(By.ID,"4v").text)
        status["gauge1"] = math.log10(float(driver.find_element(By.ID,"72v").text))
        status["gauge1"] = round(status["gauge1"] + float(driver.find_element(By.ID,"72p").text),4)
        status["gauge2"] = math.log10(float(driver.find_element(By.ID,"73v").text))
        status["gauge2"] = round(status["gauge2"] + float(driver.find_element(By.ID,"73p").text),4)
        status["watchdog"] = status["watchdog"] + 1
        if status["watchdog"] > 32765:
            status["watchdog"] = 0
        mqttc.publish(mqttTopic, json.dumps(status))
        time.sleep(2)
    except:
        runLoop = False

mqttc.loop_stop()
driver.quit()