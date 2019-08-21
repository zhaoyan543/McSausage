# Import SDK packages
import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from gpiozero import MCP3008

adc = MCP3008(channel=0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, True)

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	
host = "a329f39y597dke-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.txt"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

my_rpi = AWSIoTMQTTClient("basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("sensors/light/class2", 1, customCallback)
sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
      light = round(1024*(1.0-adc.value))
      loopCount = loopCount+1
      message = {}
      message["deviceid"] = "class2"
      import datetime as datetime
      now = datetime.datetime.now()
      message["datetimeid"] = now.isoformat()
      message["value"] = light
      import json
      my_rpi.publish("sensors/light/class2", json.dumps(message), 1)
      sleep(5)   