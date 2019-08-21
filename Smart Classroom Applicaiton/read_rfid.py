import RPi.GPIO as GPIO
import MFRC522
import signal

from rpi_lcd import LCD
from time import sleep
from gpiozero import Buzzer, LED
from picamera import PiCamera
from twilio.rest import Client

bz = Buzzer(5)
led = LED(13)
ledlate = LED(16)
ledwrong = LED(20)
ledon = LED(21)
lcd = LCD()
camera = PiCamera()
camera.resolution = (640, 480)
classid = "2"
studentinclass = []
studentspresent = ''
timein = ''

uid = None
prev_uid = None
continue_reading = True

# Twilio Phone
account_sid = "ACdbe22a0f1b0187d323b1284f4f98c242"
auth_token = "5d227f7a1873ae15b3ded53909d038a7"
client = Client(account_sid, auth_token)

my_hp = "+6597872202"
twilio_hp = "+14242864786"


# Object
class Students():
    def __init__(self, studentid=None, studentname=None, classNo=None):
        self.studentid = studentid
        self.studentname = studentname
        self.classNo = classNo

    def messages(self):
        print("Present!! Student " + self.studentname)
        lcd.text("Present! Student " + self.studentname, 1)
        sleep(5)
        lcd.clear()

student = []
student.append(Students([136, 4, 136, 80, 84], "Lim Zhao Yan", "2"))
student.append(Students([136, 4, 143, 245, 246], "Sie Wei Jie", "1"))
student.append(Students([136, 4, 139, 174, 169], "Woo Yu Xuan", "3"))



# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
mfrc522 = MFRC522.MFRC522()

# Welcome message
print ("Welcome, Please tap your card")
print ("Press Ctrl-C to stop.")

# This loop keeps checking for chips.
# If one is near it will get the UID

# SERVER SIDE

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep

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
my_rpi.subscribe("data/timein/class2", 1, customCallback)
my_rpi.subscribe("data/timeout/class2", 1, customCallback)
my_rpi.subscribe("data/student/class2", 1, customCallback)
sleep(2)

loopCount = 0

while continue_reading:
    bz.off()
    # Scan for cards    
    (status,TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)

    # If a card is found
    if status == mfrc522.MI_OK:
        bz.on()
        sleep(1)
        bz.off()
        if len(studentinclass) != 0:
                ledon.on()
        # led.on()
        # Get the UID of the card
        (status,uid) = mfrc522.MFRC522_Anticoll()
        if uid==student[0].studentid and classid == student[0].classNo:
                if len(studentinclass) != 0 and uid in studentinclass:
                        studentinclass.remove(uid)
                        if len(studentinclass) == 0:
                                ledon.off()
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        studentspresent = ''

                        sms = student[0].studentname + " has left the classroom, " + classid + ', at ' + time
                        message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['class'] = 'class 2'
                        message['timeout'] = time
                        message['attendance'] = attendance
                        my_rpi.publish("data/timeout/class2", json.dumps(message), 1)
                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

                        sleep(3)

                else:
                        studentinclass.append(uid)
                        ledon.on()
                        import datetime as datetime
                        attendance = 0
                        classtime = '08:00:00'
                        endtime = '10:00:00'
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        timein = time

                        if (classtime > time and time < endtime):
                                led.on()
                                attendance = 1
                                studentspresent = uid
                                sms = student[0].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is on time.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > classtime and time < endtime):
                                ledlate.on()
                                attendance = 2
                                studentspresent = uid
                                sms = student[0].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is late.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > endtime):
                                studentinclass = 0
                                attendance = 0
                                ledwrong.on()
                                ledon.off()

                        student[0].messages()
                # print("Lim Zhao Yan has already tapped in.")
                # lcd.text("Lim Zhao Yan has already tapped in.", 1)
                        led.off()
                        ledlate.off()
                        ledwrong.off()
                        lcd.clear()
                # led.off()
                        loopCount = loopCount+1
                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['studentname'] = student[0].studentname
                        message['class'] = 'class 2'
                        message['timein'] = time
                        message['attendance'] = attendance
                        import json
                        my_rpi.publish("data/timein/class2", json.dumps(message), 1)

                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

        elif uid==student[1].studentid and classid == student[1].classNo:
                if len(studentinclass) != 0 and uid in studentinclass:
                        studentinclass.remove(uid)
                        if len(studentinclass) == 0:
                                ledon.off()
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        studentspresent = ''

                        sms = student[1].studentname + " has left the classroom, " + classid + ', at ' + time
                        message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['class'] = 'class 2'
                        message['timeout'] = time
                        message['attendance'] = attendance
                        my_rpi.publish("data/timeout/class2", json.dumps(message), 1)
                        
                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

                        sleep(3)

                else:
                        studentinclass.append(uid)
                        ledon.on()
                        attendance = 0
                        classtime = '08:00:00'
                        endtime = '10:00:00'
                        loopCount = loopCount+1
                        import datetime as datetime
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        timein = time

                        if (classtime > time and time < endtime):
                                led.on()
                                attendance = 1
                                studentspresent = uid
                                sms = student[1].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is on time.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > classtime and time < endtime):
                                ledlate.on()
                                attendance = 2
                                studentspresent = uid
                                sms = student[1].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is late.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > endtime):
                                studentinclass = 0
                                attendance = 0
                                ledwrong.on()
                                ledon.off()

                        student[1].messages()
                        lcd.clear()
                        led.off()
                        ledlate.off()
                        ledwrong.off()

                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['studentname'] = student[1].studentname
                        message['class'] = 'class 2'
                        message['timein'] = time
                        message['attendance'] = attendance
                        import json
                        my_rpi.publish("data/timein/class2", json.dumps(message), 1)

                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

        elif uid==student[2].studentid and classid == student[2].classNo:
                if len(studentinclass) != 0 and uid in studentinclass:
                        studentinclass.remove(uid)
                        if len(studentinclass) == 0:
                                ledon.off()
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        studentspresent = ''

                        sms = student[2].studentname + " has left the classroom, " + classid + ', at ' + time 
                        message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['class'] = 'class 2'
                        message['timeout'] = time
                        message['attendance'] = attendance
                        my_rpi.publish("data/timeout/class2", json.dumps(message), 1)
                                                
                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

                        sleep(3)

                else:
                        studentinclass.append(uid)
                        ledon.on()
                        attendance = 0
                        classtime = '08:00:00'
                        endtime = '10:00:00'
                        loopCount = loopCount+1
                        import datetime as datetime
                        now = datetime.datetime.now()
                        time = now.strftime("%H:%M:%S")
                        timein = time

                        if (classtime > time and time < endtime):
                                led.on()
                                attendance = 1
                                studentspresent = uid
                                sms = student[2].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is on time.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > classtime and time < endtime):
                                ledlate.on()
                                attendance = 2
                                studentspresent = uid
                                sms = student[2].studentname + " has entered the classroom, " + classid + ', at ' + time + ', and is late.'
                                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms) 

                        if (time > endtime):
                                studentinclass = 0
                                attendance = 0
                                ledwrong.on()
                                ledon.off()

                        student[2].messages()
                        lcd.clear()
                        led.off()
                        ledlate.off()
                        ledwrong.off()

                        message = {}
                        message["deviceid"] = "class2"
                        message["datetimeid"] = now.isoformat()
                        message["studentid"] = str(uid)
                        message['studentname'] = student[2].studentname                        
                        message['class'] = 'class 2'
                        message['timein'] = time
                        message['attendance'] = attendance
                        import json
                        my_rpi.publish("data/timein/class2", json.dumps(message), 1)
                        message1 = {}
                        message1['deviceid'] = 'class2'
                        message1['datetimeid'] = now.isoformat()
                        message1['number'] = len(studentinclass)
                        my_rpi.publish("data/student/class2", json.dumps(message1), 1)

        else :
                print("You don't belong to this class!")
                print(uid)
                ledwrong.on()
                lcd.text("You don't belong to this class!", 1)
                sms = 'Someone unauthorized is trying to enter the classroom, ' + classid 
                message = client.api.account.messages.create(to=my_hp, from_=twilio_hp, body=sms)
                # camera.start_recording('/home/pi/Desktop/video1.h264')
                # camera.wait_recording(5)
                # camera.stop_recording()
                sleep(5)
                lcd.clear()
                ledwrong.off()