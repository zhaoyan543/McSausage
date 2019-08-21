#### SCHOOL OF COMPUTING (SOC)

#### ST0324 Internet of Things

# IOT CA2 McSausage Step-by-step Tutorial
## Table of Contents

- Section 1 Introduction
- Section 2 Hardware Requirements
- Section 3 Hardware Setup
- Section 4 Software Requirements
- Section 5 Software Setup Requirements
- Section 6 Project Architecture
- Section 7 Web Interface
- Section 8 How it should work
- Section 9 Bonus Feature
- Section 10 References


## Section 1 Introduction

### What is McSausage about?
This application is a smart classroom setup. With this application, more energy will be saved as the lights in a classroom will be turned off automatically once there is no one detected in the room. In addition to that, our attendance taking system will also be more secured as students would not be able to ask their friends to help them take attendance. This is because each student needs to use their own NFIC card to tap in and pass the facial recognition, in order for the system to record their attendance. If the student is early or on time, a green light will be turned on, with an attendance of on time. If they are late, a yellow light will be turned on, with an attendance of late. However, if they turn up after the class has ended, a red light will appear and their attendance will be marked as absent. If they tap their card for a wrong classroom, the red light will appear as well as a text saying ‘You don’t belong in this class!’ will appear on the LCD. A live stream video of the classroom is also available for the lecturers to double check if there is anyone in the classroom remotely.

### How it should looks like?
![Alt text](https://github.com/zhaoyan543/McSausage/blob/master/image/looks.jpeg)


## Section 2 Hardware Requirements
![Alt text](https://github.com/zhaoyan543/McSausage/blob/master/image/hardware.jpeg)

### Hardware Checklist?
| Component |	Number of Items |
| :------------------: | :---------: |
| NFC Card Reader |	1 |
| NFC Card |	Minimum 1 |
| Buzzer |	1 |
| Resistor |	5 |
| LED |	4 |
| Light Sensor w/MCP3008 ADC |	1 |
| PiCamera |  1 |
| Wire |	At least 33 |

	
## Section 3 Hardware Setup
Please do ensure that all the items is present and setup properly.
<table>
	<thead>
		<tr>
			<th> Classroom 1 to 3 </th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>LCD Screen<br>Light Sensor w/MCP3008 ADC<br>RPi PiCamera<br>Buzzer<br>RFID Card Reader<br>RFID Card<br>Green LED<br>Yellow LED x2<br>Red LED<br>Wire x35<br>Buzzer<br>Resistor x5</td>
		</tr>
	</tbody>
	</table>


## Section 4 Software Requirements
Below is a list of which library is imported to ensure that it will work properly:

<table>
  <thead>
    <tr>
      <th colspan="5"> Classroom 1 to 3 </th>
    <tr>
      <th>telegrambot.py</th>
      <th>read_rfid.py</th>
      <th>web_streaming.py</th>
      <th>lightval.py</th>
      <th>blynk.py</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>import telepot<br>from gpiozero import LED<br>time import sleep<br>from gpiozero import Buzzer<br>from rpi_lcd import LCD</td>
      <td>import RPi.GPIO as GPIO<br>import MFRC522<br>import signal<br>from rpi_lcd import LCD<br>from time import sleep<br>from gpiozero import Buzzer, LED<br>from picamera import PiCamera<br>from twilio.rest import Client</td>
      <td>import picamera<br>import io<br>import logging<br>import SocketServer<br>from threading import Condition<br>from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer</td>
      <td>import RPi.GPIO as GPIO<br>from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient<br>time import sleep<br>from gpiozero import MCP3008</td>
      <td>import time<br>from gpiozero import MCP3008, LED<br>from blynkapi import Blynk<br>from time import sleep<br>from rpi_lcd import LCD</td>
    </tr>
  </tbody>
</table>

## Section 5 Software Setup Requirements
First, to deploy the web application, the Flask library is needed to installed. The command is
```
sudo pip install flask
```
Next, since we are using PiCam. We will need to enable the camera inside raspberry pi configuration. Below are the steps to enable the camera:
 - Go to Menu
 - Preferences
 - Raspberry Pi Configuration
 - Ensure the Camera under the interface tab is enable
 - Lastly, reboot it
 
Next, to implement the LCD screen, rpi_lcd library need to be installed. The command to installed is:
```
sudo pip install rpi-lcd
```

Next, to implement NFC Card Reader and LDR to work. You will first need to ensure SPI under Raspberry Pi Configuration. In which you can follow the step from the PiCam. Which is enabled under the same place. Afterwards, you will need to install a few libraries. Which are:

<< Install Python-dev >>
```
sudo apt-get install python-dev
```
<< Install SPI-Py Library >>
```
git clone https://github.com/lthiery/SPI-Py.git
cd ~/SPI-Py
sudo python setup.py install 
```



## Section 6 Project Architecture
![Alt text](https://github.com/zhaoyan543/McSausage/blob/master/image/architecture.jpg)


## Section 7 Web Interface
### Login Page

### Main Page (Classroom 1 to 3)


## Section 8 How it should work
1) When the student tapped their card, there will be a buzzer sounding off. 
2) If the Red LED light up, it means that the student doesn't belong to the class. 
3) However, if the student were to belong in the class the student were have to face the PiCam to allow the facial recognition to check    if it matches the correct student.
4) If there is a student that had tapped in, the Yellow LED light that is not placed together with the other LED will light up to          represent classroom light being turn on.
5) If the Yellow LED among the three LED were to light up, it means that student is late. Red LED represent absent as the student tapped    in later than the class end time. Green LED represent early for class.


## Section 9 Bonus Feature


## Section 10 References

