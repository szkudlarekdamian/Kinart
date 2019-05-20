import numpy as np
import cv2
from threading import Thread, Event
import config
import globals
import kinect_video_recorder as kin
import GUI



class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.found = 1
        self.isRunning = False

    def run(self):
        self.isRunning = True

        while not self.stopped.wait(config.CHECKING_FOR_HAND_INTERVAL):
            if config.MINIMUM_VALUE_TO_CONSIDER_HAND <= globals.CENTER_VALUE <= config.MAXIMUM_VALUE_TO_CONSIDER_HAND:
                self.found += 1
            else:
                self.found = 1
            if self.found == config.HOW_MANY_TIMES_HAND_MUST_BE_FOUND + 1:
                self.isRunning = False
                self.stopped.set()


class HandTracker(object):
    def __init__(self):
        # self.cap.set(cv2.CAP_PROP_POS_MSEC, 100000)

        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.handInitialized = False

        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # self.writer = cv2.VideoWriter("MOSSE.avi", self.fourcc, 10.0, (640, 480), True)

        self.tracker = cv2.TrackerCSRT_create()

        self.stopFlag = Event()
        self.thread = MyThread(self.stopFlag)

        self.x1 = int(self.width * 0.3)
        self.x2 = int(self.width * 0.46)
        self.y1 = int(self.height * 0.15)
        self.y2 = int(self.height * 0.35)

        self.centerPoint = [(self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2]

    def initCap(source):
        self.cap = cv2.VideoCapture(source)

    def kinectOpened(self):
        return self.cap.isOpened()

    def getNextFrame(self):
        frameLoaded, frame = self.cap.read()
        if not frameLoaded:
            return None
        return frame

    def getFrameWithInitBox(self, frame, drawHand=config.SHOW_INIT_HAND_CONTOUR):
        frameCopy = frame.copy()
        if drawHand:
            frameCopy = drawContour(frameCopy, globals.HAND_CONTOUR)
        cv2.circle(frameCopy, (self.centerPoint[0], self.centerPoint[1]), 3, config.CENTER_POINT_COLOR_INIT, 2)
        cv2.rectangle(frameCopy, (self.x1, self.y1), (self.x2, self.y2), config.BOUNDING_BOX_COLOR_INIT,
                      config.BOUNDING_BOX_BORDER_WIDTH, 2)
        return frameCopy

    def filterDepth(self, frame, closestDistant, furthestDistant):
        return (np.where(((frame <= furthestDistant) & (frame >= closestDistant)), 128, 0)).astype(np.uint8)

    def enhanceFrame(self, frame):
        frameCopy = frame.copy()
        np.clip(frameCopy, 0, 2 ** 10 - 1, frameCopy)
        frameCopy >>= 2
        return frameCopy.astype(np.uint8)

    @staticmethod
    def getNeighbourhoodROI(frame, centerPoint, side):
        lowerHeight = centerPoint[1] - side // 2
        upperHeight = centerPoint[1] + side // 2
        lowerWidth = centerPoint[0] - side // 2
        upperWidth = centerPoint[0] + side // 2
        return frame[lowerHeight:upperHeight, lowerWidth:upperWidth]

    def getValueOfCenter(self, frame):
        frameCopy = self.enhanceFrame(frame)
        frameCopy = cv2.cvtColor(frameCopy, cv2.COLOR_BGR2GRAY)
        center = self.getNeighbourhoodROI(frameCopy, self.centerPoint, config.MEDIAN_SQUARE_SIDE)
        median = np.median(center)
        return median

    def filterFrame(self, frame, center, condition=2, kernelSize=3, iterations=1):
        frameCopy = frame.copy()
        frameCopy = cv2.cvtColor(frameCopy, cv2.COLOR_BGR2GRAY)
        frameCopy = higlightRectangleInImage(frameCopy, (self.x1, self.y1), (self.x2, self.y2), 10)
        median = np.uint8(np.median(center))
        frameCopy = frameCopy.astype(np.int)
        frameCopy = np.where((abs(frameCopy - int(median)) <= condition), 128, 0)
        frameCopy = frameCopy.astype(np.uint8)
        return self.morphClose(frameCopy, kernelSize=kernelSize, iterations=iterations)

    def morphClose(self, frame, kernelSize=3, iterations=1):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernelSize, kernelSize))
        return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    def floodFill(self, frame):
        mask = np.zeros((self.height + 2, self.width + 2), np.uint8)
        flood = frame.copy()
        cv2.floodFill(flood, mask, (self.centerPoint[0], self.centerPoint[1]), 255)
        return flood

    def findHandContour(self, frame, drawContour=False):
        frameCopy = frame.copy()
        contours = cv2.findContours(frameCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        if cv2.__version__[0] == '3':
            contours = cv2.findContours(frameCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
        max_contour = max(contours, key=cv2.contourArea)
        moment = cv2.moments(max_contour)
        if moment['m00'] != 0:
            cx = int(moment['m10'] / moment['m00'])
            cy = int(moment['m01'] / moment['m00'])
        boundRect = cv2.boundingRect(max_contour)
        if drawContour:
            img = cv2.cvtColor(frameCopy, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(img, max_contour, -1, (0, 102, 255), 2)
            cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
            cv2.rectangle(img, (int(boundRect[0]), int(boundRect[1])),
                          (int(boundRect[0] + boundRect[2]), int(boundRect[1] + boundRect[3])), (255, 255, 0), 2)
            return img, max_contour, boundRect
        return max_contour, boundRect

    def initTracker(self, frame):
        frame = self.enhanceFrame(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center = self.getNeighbourhoodROI(gray, self.centerPoint, 40)
        filtered = self.filterFrame(frame, center)
        # showPausedImage(filtered)
        flood = self.floodFill(filtered)
        # showPausedImage(flood)
        img, max_contour, boundingBox = self.findHandContour(flood, drawContour=True)
        # showPausedImage(img)

        # self.gestureRecognition(flood, (self.x1,self.y1), (self.x2, self.y2))
        self.tracker.init(filtered, boundingBox)

    def gestureRecognition(self, frame, p1, p2, offset=5):
        image = frame.copy()

        image = higlightRectangleInImage(image, p1, p2, offset)

        max_contour, _ = self.findHandContour(image)
        img_draw = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        hull = cv2.convexHull(max_contour, returnPoints=False)
        defects = cv2.convexityDefects(max_contour, hull)

        num_fingers = 1
        print(cv2.contourArea(max_contour))
        for i in range(defects.shape[0]):
            start_index, end_index, farthest_index, _ = defects[i, 0]
            start = tuple(max_contour[start_index][0])
            end = tuple(max_contour[end_index][0])
            far = tuple(max_contour[farthest_index][0])

            cv2.line(img_draw, start, end, (0, 255, 0), 2)
            # print(angle_rad(np.subtract(start, far), np.subtract(end, far)))
            if angle_rad(np.subtract(start, far), np.subtract(end, far)) < 80:
                num_fingers += 1

            # print(num_fingers)
        if num_fingers == 1:
            cv2.putText(img_draw, str(num_fingers) + " FIST " + str(defects.shape[0]), (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            num_fingers = 0
        else:
            cv2.putText(img_draw, str(num_fingers) + " OPEN HAND " + str(defects.shape[0]), (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            num_fingers = 1

        # cv2.imshow("Hulls", img_draw)
        return max_contour, num_fingers

    def trackHand(self, frame):
        # if self.writer is None:
        #     self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        #     self.writer = cv2.VideoWriter("outputAA.avi", self.fourcc, 10.0,
        #                              (frame.shape[1], frame.shape[0]), True)
        color = frame.copy()
        frame = self.enhanceFrame(frame)

        frame = self.filterDepth(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), config.CLOSEST_DISTANCE,
                                 config.FURTHEST_DISTANCE)

        # cv2.imshow("Filtered", frame)
        # cv2.waitKey(0)

        trackerUpdated, boundRect = self.tracker.update(frame)
        if trackerUpdated:
            # Pomyślny tracking
            p1 = (int(boundRect[0]), int(boundRect[1]))
            p2 = (int(boundRect[0] + boundRect[2]), int(boundRect[1] + boundRect[3]))

            contour, gesture = self.gestureRecognition(frame, p1, p2)
            #cv2.drawContours(color, contour, -1, (0, 255, 0), 2)
            cv2.rectangle(color, p1, p2, config.BOUNDING_BOX_COLOR_TRACKING, config.BOUNDING_BOX_BORDER_WIDTH, 1)
            cv2.circle(color, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2), 3, config.CENTER_POINT_COLOR_TRACKING, -1)
            coords = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

        else:
            # Tracking failure
            cv2.putText(color, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            coords = None
        if coords is not None:
            if gesture == 0:
                gestureName = "FIST"
            else:
                gestureName = "OPEN HAND"
            cv2.putText(color, gestureName + ' (' + str(coords[0]) + ',' + str(coords[1]) + ')', (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 0, 255), 2)
        else:
            cv2.putText(color, '(None, None)', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        # self.writer.write(color)
        color = self.getFrameWithInitBox(color, False)
        return color, coords, gesture


def angle_rad(v1, v2):
    return np.rad2deg(np.arctan2(np.linalg.norm(np.cross(v1, v2)), np.dot(v1, v2)))


def higlightRectangleInImage(image, p1, p2, offset=0, grayValue=0):
    imageCopy = image.copy()
    height, width = image.shape[0:2]
    for x in range(width):
        for y in range(height):
            if (x < p1[0] - offset or y < p1[1] - offset) or (x > p2[0] + offset or y > p2[1] + offset):
                imageCopy[y, x] = grayValue
    return imageCopy


def drawContour(image, contour, color=(0, 0, 255)):
    imageCopy = image.copy()
    previousPoint = contour[0]
    for point in contour:
        cv2.line(imageCopy, previousPoint, point, color, 2)
        previousPoint = point
    return imageCopy


def showPausedImage(image):
    cv2.imshow("Image", image)
    cv2.waitKey(0)

if __name__ == "__main__":
    # Ścieżka do filmu z mapą głębi lub ID kamery
    videoPath = "/home/ciasterix/Kodzenie/Kinect/Kinart/videokinec_depth13.avi"

    frame = kin.get_depth_with_3rd_layer()
    
    paint = GUI.Kinart()

    # Obiekt klasy HandTracker, której głównym zadaniem jest zwracanie współrzędnych dłoni, na podstawie filmu mapy głębi
    hT = HandTracker(videoPath)
    print("start")

    while hT.kinectOpened():
        print("petla")

        cv2.waitKey(20)
        # hT.cap.set(cv2.CAP_PROP_POS_MSEC, 39550)
        # Sztuczne spowolnienie klatek, tylko do celów testowych
        # Pobieranie kolejnej klatki
        # frame = hT.getNextFrame()
        # print(frame)
        frame = kin.get_depth_with_3rd_layer()
        # Jeśli klatka została wczytana poprawnie to kontynuuj
        if frame is not None:
            # Jeśli dłoń nie została jeszcze zainicjalizowana do systemu
            if hT.handInitialized is False:
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
            # #Jeśli dłoń została zainicjalizowana to
            else:
                # Śledź dłoń i uzyskaj jej współrzędne
                frameWithCoords, coords, gesture = hT.trackHand(frame)
                cv2.imshow('Kinart', frameWithCoords)

                if coords != None:
                    print("_____ GUI ______")
                    print(coords)

                    if coords[0] < 0:
                        print("Wrong coords !")
                    elif coords[0] > 640:
                        print("Wrong coords !")
                    elif coords[1] <= 0:
                        print("Wrong coords !")
                    elif coords[1] > 480:
                        print("Wrong coords !")
                    elif coords[1] > 0 and coords[1] <= 50:
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
                    else:
                        # print(coords)
                        # print(paint.getWindowSize())
                        paint.updateCoords((640 - coords[0]), (coords[1] - 50))

                else:
                    print("NONE coords")
        else:
            break
