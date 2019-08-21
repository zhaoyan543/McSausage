import telepot
from gpiozero import LED
from time import sleep
from gpiozero import Buzzer
from rpi_lcd import LCD


my_bot_token = '871241289:AAFdaGcVFeXtRq394QafXq1T2zpCTLt52C8'

led = LED(21)
buzzer = Buzzer(5)
lcd = LCD()

def alert():
   led.on()
   buzzer.on()
   sleep(1)
   buzzer.off()
   lcd.text('Turning on',1)
   lcd.text('Classroom',2)
   sleep(3)
   lcd.text('',1)
   lcd.text('',2)

   return "Got it, turning on the classroom."

def false():
   led.off()
   buzzer.on()
   sleep(1)
   buzzer.off()
   lcd.text('Turning off',1)
   lcd.text('Classroom.',2)
   sleep(3)
   lcd.text('',1)
   lcd.text('',2)

   return "Got it, turning off the classroom."

def respondToMsg(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print('Got command: {}'.format(command))

    if command == 'on':
       bot.sendMessage(chat_id, alert())
    elif command =='off':
       bot.sendMessage(chat_id, false())

bot = telepot.Bot(my_bot_token)
bot.message_loop(respondToMsg)
print('Waiting for commands...')

while True:
     sleep(10)