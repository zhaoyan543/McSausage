import time
from gpiozero import MCP3008, LED
from blynkapi import Blynk
from time import sleep
from rpi_lcd import LCD

auth_token = "1letPRLrzfboQtbakpFaOk2dX_vc-xCg"

led = LED(21)
adc = MCP3008(channel=0)
lcd = LCD()

while True:
  try:

    button = Blynk(auth_token, pin = "V0")
    button_val = str(button.get_val()[0])
    print("Button value is %s" %(button_val))
    if button_val=="1":
      led.on()
      lcd.text('Classroom is open', 1)
    else:
      led.off()
      lcd.text('', 1)

    light = Blynk(auth_token, pin = "V1")
    light_sensor_value = adc.value*1024
    s_light_sensor_value = str(light_sensor_value)
    fs_light_sensor_value = "[\""+ s_light_sensor_value+"\"]"
    print("Light sensor value is %s" %(fs_light_sensor_value))
    light.set_val_old(fs_light_sensor_value)

    time.sleep(1)

  except KeyboardInterrupt:
    print "Program aborted"
    sys.exit()

  except:
    print "Unexpected error:", sys.exc_info()[0]
    sys.exit()