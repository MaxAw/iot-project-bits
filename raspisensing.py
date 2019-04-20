import time

import RPi.GPIO as GPIO
import raspitointel as transmitter

# GPIO setup
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)


def callback(channel):
    if GPIO.input(channel):
        data = "Motion detected"
    else:
        data = "Motion detected"

    writeToFile(data)


def writeToFile(data):

    # open file to write data (will overwrite old data)
    file_name = 'datafile.txt'
    data_file = open(file_name, 'w')

    # write data with timestamp
    data_with_timestamp = time.ctime() + " - " + data
    data_file.write(data_with_timestamp)

    # save file contents
    data_file.close()


GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

while True:
    time.sleep(1)
