from flask import Flask, render_template, Response, jsonify, request
import Adafruit_DHT
from rpi_lcd import LCD
import sys

import json
import numpy
import datetime
import decimal

import mysql.connector
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep

import dynamodb
import jsonconverter as jsonc



global currentLightValue



gevent.monkey.patch_all()


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


# Custom MQTT message callback
def customCallback(client, userdata, message):
    jsonMsg = json.loads(message.payload)
    global currentLightValue
    currentLightValue = jsonMsg["value"]
    print(currentLightValue)
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")



# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("sensors/light/class1", 1, customCallback)
sleep(2)

# Publish to the same topic in a loop forever
# loopCount = 0
# while True:
#     light = round(1024-(adc.value*1024))
#     my_rpi.publish("sensors/light", str(light), 1)
#     sleep(5)


class GenericEncoder(json.JSONEncoder):
    
    def default(self, obj):  
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj) 
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:  
            return json.JSONEncoder.default(self, obj) 

def data_to_json(data):
    json_data = json.dumps(data,cls=GenericEncoder)
    return json_data

def connect_to_mysql(host,user,password,database):
    try:
        cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)

        cursor = cnx.cursor()
        print("Successfully connected to database!")

        return cnx,cursor

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

        return None

def fetch_fromdb_as_json(cnx,cursor,sql):
    
    try:
        cursor.execute(sql)
        row_headers=[x[0] for x in cursor.description] 
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers,result)))
        
        data_reversed = data[::-1]

        data = {'data':data_reversed}

        return data_to_json(data)

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None



app = Flask(__name__)


@app.route("/api/getdata",methods=['POST','GET'])
def apidata_getdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb()), 
             'title': "IOT Data"}
            return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


# @app.route("/api/getdata",methods = ['POST', 'GET'])
# def apidata_getdata():
#     if request.method == 'POST':
#         try:
#             host='localhost'; user='ca1user'; password='Wyx123456'; database='ca1Database';
#             sql="SELECT datetime, temp, humidity FROM environmentData ORDER BY datetime DESC LIMIT 10"
#             cnx,cursor = connect_to_mysql(host,user,password,database)
#             json_data = fetch_fromdb_as_json(cnx,cursor,sql)
#             loaded_r = json.loads(json_data)
#             data = {'chart_data': loaded_r, 'title': "IOT Data"}
#             return jsonify(data)
#         except:
#             print(sys.exc_info()[0])
#             print(sys.exc_info()[1])



@app.route('/')
def index():
    # Video streaming home page.
    return render_template('index.html')

lcd = LCD()
lcd.text('Im around, press', 1)
lcd.text('the door bell.', 2)

def displayAround():
    lcd.text('Im around, press', 1)
    lcd.text('the door bell.', 2)
    return 'Im around, press the door bell.'

def displayNotAround():
    lcd.text('Sorry,', 1)
    lcd.text('Im not around ', 2)
    return 'Sorry, Im not around.'



@app.route("/getCurrentReadings")
def getReadings():
    humidity, temperature = Adafruit_DHT.read_retry(11, 19)
    humidityStr = str(humidity) + "," + str(temperature)
    return humidityStr



@app.route("/writeLCD/<status>")
def writePin(status):
    print(status)
    if status == 'yes':
        response = displayAround()
    else:
        response = displayNotAround()
    return response



@app.route("/getCurrentLightValue")
def getCurrentLightValue():
    global currentLightValue
    msg = str(currentLightValue)
    return msg



if __name__ == '__main__':
   try:
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        http_server.serve_forever()
        print('Server waiting for requests')
   except:
        print("Exception")
        import sys
        print(sys.exec_info()[0])
        print(sys.exec_info()[1])
    
