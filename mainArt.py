from handTracker import *
import config
import globals
import GUI
import kinect_video_recorder as kin
import numpy as np
import cv2

class Gesture(object):
    def __init__(self, startGesture=1, historyLen=5):
        self.currentGesture = startGesture
        self.gestureHistory = [startGesture]*historyLen

    def getGesture(self):
        return self.currentGesture

    def checkGesture(self, newGesture):
        print(self.gestureHistory)
        self.gestureHistory = self.gestureHistory[1:]
        self.gestureHistory.append(newGesture)
        print(self.gestureHistory)
        print(self.currentGesture)
        print(" ")
        if len(set(self.gestureHistory)) == 1:
            self.currentGesture = self.gestureHistory[0]
        elif len(set(self.gestureHistory)) != 2:
            raise Exception('Error in gestureHistory')


def initializeHandWithFrame(hT, frame):
    '''
    param1 : Instance of handTracker
    '''
    globals.CENTER_VALUE = hT.getValueOfCenter(frame)
    print("Center get value", hT.getValueOfCenter(frame))
    # Pokaż klatkę z narysowaną przestrzenią na dłoń
    cv2.imshow('Kinart', hT.getFrameWithInitBox(frame))
    # Jeśli wątek jest już uruchomiony
    if hT.thread.isRunning:
        # print("Hand found in thread: "+str(hT.thread.found))
        if hT.thread.found == config.HOW_MANY_TIMES_HAND_MUST_BE_FOUND:
            print("Hand initialized")
            hT.initTracker(frame)
            hT.handInitialized = True
    else:
        print("Searching for hand")
        hT.stopFlag.clear()
        hT.thread = MyThread(hT.stopFlag)
        hT.thread.start()


def checkCoordsCorrectness(coords):
    '''
    param1 : coordinates as a touple of two integers
    retruns: true if coorinates are correct and false otherwise
    '''
    if coords[0] < 0 or coords[0] > 640:
        return False
    elif coords[1] <= 0 or coords[1] > 480:
        return False
    return True


def useInterfaceButton(paint, coords):
    '''
    param1 : instance of Kinart class from GUI
    param2 : coordinates as tuple of integers
    '''
    if coords[0] > 0 and coords[0] <= 130:
        print("Black Button")
        paint.black_color()
    if coords[0] > 130 and coords[0] <= 230:
        print("Blue Button")
        paint.blue_color()
    if coords[0] > 230 and coords[0] <= 330:
        print("Red Button")
        paint.red_color()
    if coords[0] > 330 and coords[0] <= 430:
        print("Green Button")
        paint.green_color()
    if coords[0] > 430 and coords[0] <= 530:
        print("Eraser Button")
        paint.eraser_button()
    if coords[0] > 530 and coords[0] < 640:
        print("Pen Button")
        paint.pen_button()


def paintAndinteract(paint, coords, gest):
    print("_____ GUI ______")
    print(coords)

    if not checkCoordsCorrectness:
        print("Wrong coords !")
    elif coords[1] > 0 and coords[1] <= 50:
        useInterfaceButton(paint, coords)
    #Jeśli gest nie jest pięścią
    elif gest.getGesture() != 0:
        # print(coords)
        # print(paint.getWindowSize())
        paint.updateCoords((640 - coords[0]), (coords[1] - 50))
    # Jeśli gest jest pięścią
    else:
        paint.reset()
        print("piasteczka piasteczka piatunia")


if __name__ == "__main__":
    source = 'kinect'
    # source = 'video'

    videoPath = "/home/ciasterix/Kodzenie/Kinect/Kinart/videokinec_depth13.avi"

    if source == 'video':
        videoPath = "/home/ciasterix/Kodzenie/Kinect/Kinart/videokinec_depth13.avi"
    else:
        frame = kin.get_depth_with_3rd_layer()
    
    # Obiekt klasy HandTracker, której głównym zadaniem jest zwracanie współrzędnych dłoni, na podstawie filmu mapy głębi
    hT = HandTracker(videoPath)
    paint = GUI.Kinart()
    gest = Gesture()

    while hT.kinectOpened():
        cv2.waitKey(20)

        # Pobieranie kolejnej klatki
        if source == 'video':
            hT.cap.set(cv2.CAP_PROP_POS_MSEC, 39550)
            frame = hT.getNextFrame()
        else:
            frame = kin.get_depth_with_3rd_layer()

        # Jeśli klatka została wczytana poprawnie to kontynuuj
        if frame is not None:
            # Jeśli dłoń nie została jeszcze zainicjalizowana do systemu
            if hT.handInitialized is False:
                initializeHandWithFrame(hT, frame)
            # #Jeśli dłoń została zainicjalizowana to
            else:
                # Śledź dłoń i uzyskaj jej współrzędne
                frameWithCoords, coords, gesture = hT.trackHand(frame)
                gest.checkGesture(gesture)
                cv2.imshow('Kinart', frameWithCoords)

                if coords != None:
                    paintAndinteract(paint, coords, gest)
                else:
                    print("NONE coords")
        else:
            break
