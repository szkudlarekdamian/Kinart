import numpy as np
import cv2
from threading import Thread, Event
import time

#KEY OPTIONS
checkingForHandInterval = 1
howManyTimesHandMustBeFound = 5
minimumValueToConsiderHand = 14
maximumValueToConsiderHand = 17

boundingBoxColorInit = (177, 187, 223)
centerPointColorInit = (118, 100, 245)
boundingBoxColorTracking = (173,245,145)
centerPointColorTracking = (239,237,191)


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.found = 1
        self.isRunning = False

    def run(self):
        self.isRunning = True
        global centerValue
        while not self.stopped.wait(checkingForHandInterval):
            #print(centerValue)
            if minimumValueToConsiderHand <= centerValue <= maximumValueToConsiderHand:
                self.found += 1
            else:
                self.found = 1
                #self.stopped.set()
            if self.found == howManyTimesHandMustBeFound+1:
                self.isRunning = False
                self.stopped.set()

class HandTracker(object):
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, 39500)

        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.handInitialized = False

        #self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #self.writer = cv2.VideoWriter("MOSSE.avi", self.fourcc, 10.0, (640, 480), True)

        self.tracker = cv2.TrackerCSRT_create()

        self.stopFlag = Event()
        self.thread = MyThread(self.stopFlag)

        self.x1 = int(self.width * 0.3)
        self.x2 = int(self.width * 0.46)
        self.y1 = int(self.height * 0.15)
        self.y2 = int(self.height * 0.35)

        self.centerPoint = [(self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2]

    def kinectOpened(self):
        return self.cap.isOpened()

    def getNextFrame(self):
        frameLoaded, frame = self.cap.read()
        if not frameLoaded:
            return None
        return frame

    def getFrameWithInitBox(self, frame):
        cv2.circle(frame, (self.centerPoint[0], self.centerPoint[1]), 3, centerPointColorInit, 2)
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), boundingBoxColorInit, 2)
        return frame

    def filterDepth(self, frame, closestDistant, furthestDistant):
        return (np.where(((frame <= furthestDistant) & (frame >= closestDistant)), 128, 0)).astype(np.uint8)

    def enhanceFrame(self, frame):
        frameCopy = frame.copy()
        np.clip(frameCopy, 0, 2 ** 10 - 1, frameCopy)
        frameCopy >>= 2
        return frameCopy.astype(np.uint8)

    def getNeighbourhoodROI(self, frame, centerPoint, side):
        lowerHeight = centerPoint[1] - side // 2
        upperHeight = centerPoint[1] + side // 2
        lowerWidth = centerPoint[0] - side // 2
        upperWidth = centerPoint[0] + side // 2
        return frame[lowerHeight:upperHeight, lowerWidth:upperWidth]

    def getValueOfCenter(self, frame):
        frame = self.enhanceFrame(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center = self.getNeighbourhoodROI(frame, self.centerPoint, 60)
        median = np.median(center)
        return median


    def filterFrame(self, frame, center, condition=5, kernelSize=3, iterations=1):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        median = np.uint8(np.median(center))
        frame = frame.astype(np.int)
        frame = np.where((abs(frame - int(median)) <= condition), 128, 0)
        frame = frame.astype(np.uint8)
        return self.morphClose(frame, kernelSize=kernelSize, iterations=iterations)

    def morphClose(self, frame, kernelSize=3, iterations=1):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernelSize, kernelSize))
        return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    def floodFill(self, frame):
        mask = np.zeros((self.height + 2, self.width + 2), np.uint8)
        flood = frame.copy()
        cv2.floodFill(flood, mask, (self.centerPoint[0], self.centerPoint[1]), 255)
        return flood

    def findHandContour(self, frame, drawContour=False):
        contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        if cv2.__version__[0] == '3':
            contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
        max_contour = max(contours, key=cv2.contourArea)
        moment = cv2.moments(max_contour)
        if moment['m00'] != 0:
            cx = int(moment['m10'] / moment['m00'])
            cy = int(moment['m01'] / moment['m00'])
        boundRect = cv2.boundingRect(max_contour)
        if drawContour:
            img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(img, max_contour, -1, (0, 102, 255), 2)
            cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
            cv2.rectangle(img, (int(boundRect[0]), int(boundRect[1])),
                          (int(boundRect[0] + boundRect[2]), int(boundRect[1] + boundRect[3])), (255, 255, 0), 2)
            return img, max_contour, [cx, cy], boundRect
        return max_contour, [cx, cy], boundRect

    def initTracker(self, frame):
        frame = self.enhanceFrame(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center = self.getNeighbourhoodROI(gray, self.centerPoint, 40)
        filtered = self.filterFrame(frame, center)
        flood = self.floodFill(filtered)
        img, boundingBox = self.findHandContour(flood, drawContour=True)[0:4:3]
        self.tracker.init(filtered, boundingBox)

    def trackHand(self, frame):
        # if self.writer is None:
        #     self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        #     self.writer = cv2.VideoWriter("outputAA.avi", self.fourcc, 10.0,
        #                              (frame.shape[1], frame.shape[0]), True)
        color = frame.copy()
        frame = self.enhanceFrame(frame)

        frame = self.filterDepth(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 10, 30)

        trackerUpdated, boundRect = self.tracker.update(frame)
        if trackerUpdated:
            #Pomyślny tracking
            p1 = (int(boundRect[0]), int(boundRect[1]))
            p2 = (int(boundRect[0] + boundRect[2]), int(boundRect[1] + boundRect[3]))
            cv2.rectangle(color, p1, p2, boundingBoxColorTracking, 2, 1)
            cv2.circle(color, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2), 3, centerPointColorTracking, -1)
            coords = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

        else:
            # Tracking failure
            cv2.putText(color, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),2)
            coords = None
        if coords is not None:
            cv2.putText(color, '('+str(coords[0])+','+str(coords[1])+')', (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
        else:
            cv2.putText(color, '(None, None)', (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
        # self.writer.write(color)
        return color, coords


#Ścieżka do filmu z mapą głębi lub ID kamery
videoPath = "C:\\Users\\Damian\\Documents\\Studia\\PT\\Kinart\\videokinec_depth4_v2.avi"

#Obiekt klasy HandTracker, której głównym zadaniem jest zwracanie współrzędnych dłoni, na podstawie filmu mapy głębi
hT = HandTracker(videoPath)
centerValue = 0

while(hT.kinectOpened()):
    cv2.waitKey(100)
    hT.cap.set(cv2.CAP_PROP_POS_MSEC, 39550)
    #Sztuczne spowolnienie klatek, tylko do celów testowych
    #Pobieranie kolejnej klatki
    frame = hT.getNextFrame()
    #Jeśli klatka została wczytana poprawnie to kontynuuj
    if frame is not None:
        #Jeśli dłoń nie została jeszcze zainicjalizowana do systemu
        if hT.handInitialized is False:
            centerValue = hT.getValueOfCenter(frame)
        # Pokaż klatkę z narysowaną przestrzenią na dłoń
            cv2.imshow('Kinart',hT.getFrameWithInitBox(frame))
        # Jeśli wątek jest już uruchomiony
            if hT.thread.isRunning:
                # print("Hand found in thread: "+str(hT.thread.found))
                if hT.thread.found == howManyTimesHandMustBeFound:
                    print("Hand initialized")
                    hT.initTracker(frame)
                    hT.handInitialized = True
            else:
                print("Searching for hand")

                hT.stopFlag.clear()
                hT.thread = MyThread(hT.stopFlag)
                hT.thread.start()
        # #Jeśli dłoń została zainicjalizowana to
        else:
            #Śledź dłoń i uzyskaj jej współrzędne
            frameWithCoords, coords = hT.trackHand(frame)
            cv2.imshow('Kinart', frameWithCoords)
    else:
        break
