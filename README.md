# robogo: our robotic tank!!
created for cs fair by left no scrums (lily toledo, kayla wang, mandy wu, and christine yu)

## prerequisites:
python 3.x (on both devices)

on pc: tkinter, numpy, opencv-python, PIL, requests, sqlite3 

on raspberry pi: flask, adafruit-motorkit, numpy, opencv-python

to install required packages on pc:  

` pip3 install opencv-python numpy pillow requests `

for raspberry pi:

` pip3 install flask adafruit-motorkit opencv-python `

## how to run
make sure you run this in order! 

on raspberry pi:

` cd RaspPiFiles && python3 main.py `

then:
- wait a few seconds to ensure api is up & running
- check if the api url matches the ones defined at the beginning of Automation.py and GUI.py
- check console log to see if video frames are successfully being posted to API 

then, on pc:

` cd ComputerFiles && python3 main.py `
