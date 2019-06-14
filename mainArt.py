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
        # print(self.gestureHistory)
        self.gestureHistory = self.gestureHistory[1:]
        self.gestureHistory.append(newGesture)
        # print(self.gestureHistory)
        # print(self.currentGesture)
        # print(" ")
        if len(set(self.gestureHistory)) == 1:
            self.currentGesture = self.gestureHistory[0]
        elif len(set(self.gestureHistory)) != 2:
            raise Exception('Error in gestureHistory')


def initializeHandWithFrame(hT, frame):
    '''
    param1 : Instance of handTracker
    param2 : picture as numpy array
    '''
    globals.CENTER_VALUE = hT.getValueOfCenter(frame)
    # print("Center get value", hT.getValueOfCenter(frame))
    
    if config.MINIMUM_VALUE_TO_CONSIDER_HAND > globals.CENTER_VALUE:
        # print('too close')
        frame = writeDistanceInfoOnFrame(frame, 'too close')
    elif globals.CENTER_VALUE > config.MAXIMUM_VALUE_TO_CONSIDER_HAND:
        # print('too far')
        frame = writeDistanceInfoOnFrame(frame, 'too far')

    # Pokaż klatkę z narysowaną przestrzenią na dłoń
    frame = hT.getFrameWithInitBox(frame)
    cv2.imshow('Kinart', frame)
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


def writeDistanceInfoOnFrame(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (50,50)
    fontScale = 1
    fontColor = (255,0,0)
    lineType = 2
    cv2.putText(frame, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
    return frame



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
    if coords[0] > 0 and coords[0] <= 90:  # 130
        #print("SAVE Button")
        paint.save()
    if coords[0] > 90 and coords[0] <= 180:  # 130
        #print("Black Button")
        paint.black_color()
    if coords[0] > 180 and coords[0] <= 270:
        #print("Blue Button")
        paint.blue_color()
    if coords[0] > 270 and coords[0] <= 360:
        #print("Red Button")
        paint.red_color()
    if coords[0] > 360 and coords[0] <= 450:
        #print("Green Button")
        paint.green_color()
    if coords[0] > 450 and coords[0] <= 530:
        #print("Eraser Button")
        paint.use_eraser()
    if coords[0] > 530 and coords[0] < 640:
        #print("Pen Button")
        paint.resetCanvas()


def paintAndinteract(paint, coords, gest):
    # print("_____ GUI ______")
    # print(coords)

    if not checkCoordsCorrectness:
        print("Wrong coords !")
    elif coords[1] > 0 and coords[1] <= 50:
        useInterfaceButton(paint, coords)
    #Jeśli gest nie jest pięścią
    elif gest.getGesture() != 0:
        # print(coords)
        # print(paint.getWindowSize())
        paint.resetDot()
        paint.updateCoords((640 - coords[0]), (coords[1] - 50))
    # Jeśli gest jest pięścią
    else:
        paint.reset()
        paint.createDot((640 - coords[0]), (coords[1] - 50))
        # print("piasteczka piasteczka piatunia")


def rescale_coords(coords, scale=2):
    # print("")
    # print("old_coords:", coords)
    coords = list(coords)
    coords[0] -= 640 / (2 * scale)
    coords[0] *= scale
    coords[0] = int(coords[0])
    coords[1] -= 480 / (2 * scale)
    coords[1] *= scale
    coords[1] = int(coords[1])

    if coords[0] > 640:
        coords[0] = 640
    elif coords[0] < 0:
        coords[0] = 0

    if coords[1] > 480:
        coords[1] = 480
    elif coords[1] < 0:
        coords[1] = 0

    coords = tuple(coords)    
    # print("new_coords:", coords)    
    return coords


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
                paint.resetDot()
                initializeHandWithFrame(hT, frame)
            # #Jeśli dłoń została zainicjalizowana to
            else:
                # Śledź dłoń i uzyskaj jej współrzędne
                frameWithCoords, coords, gesture = hT.trackHand(frame)
                gest.checkGesture(gesture)
                cv2.imshow('Kinart', frameWithCoords)

                if coords != None:
                    coords = rescale_coords(coords)
                    paintAndinteract(paint, coords, gest)
                else:
                    print("NONE coords")
                    hT.tracker = cv2.TrackerCSRT_create()
                    hT.handInitialized = False
        else:
            break
