import cv2
import numpy as np
import time
from math import sqrt, tan, radians, asin, atan2
from pprint import pprint
import glm
import time
import params
from tracker import Tracker, full_img_width, full_img_height, fb_zoom
from time import sleep


tracker = Tracker()

while True:

    # rotMatObj = findRotMat(instrVecOrig, instrVec)
    instrPos, instrDir = tracker.getInstrCoords()
    if (img := tracker.last_img) is not None:
        img = cv2.resize(
            img,
            (full_img_width // fb_zoom, full_img_height // fb_zoom),
            interpolation=cv2.INTER_AREA,
        )
        cv2.imshow("Test", img)
        if instrPos is None:
            print("Instrument not detected")
        else:
            print("Pos", instrPos)
            print("Dir", instrDir)
    else:
        if not tracker._isConnected():
            print("Waiting for connection")
        else:
            print("Waiting for image")
        sleep(1)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
