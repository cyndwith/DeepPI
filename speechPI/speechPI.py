import speech_recognition as sr
from movement_control import *
import time

recog = sr.Recognizer()

mic = sr.Microphone()
car=CarControl()
while 1:
    with mic as source:
        recog.adjust_for_ambient_noise(source)
        print("Say Something ... !\n")
        audio = recog.listen(source)
        print(" Processing Audio ... ! \n")

    try:
        text = recog.recognize_google(audio)
        text=text.lower()
        print("You said ", text)
        
        if "left" in text:
            car.steer_left(30)
        if "right" in text:
            car.steer_right(30)
        if "legend" in text:
            car.steer_left(30)
            time.sleep(1)
            car.steer_right(30)
            time.sleep(1)
            car.steer_left(0)
            
            

    except sr.UnknownValueError:
        print("Could not understand your command !\n")
    except sr.RequestError as e:
        print("Speech Recognition {0}".format(e))
        break
    
