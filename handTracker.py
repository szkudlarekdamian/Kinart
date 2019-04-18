import numpy as np
import cv2
import time

class HandTracker(object):
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, 39500)

        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        self.tracker = cv2.TrackerMedianFlow_create()

        x1 = int(self.width * 0.3)
        x2 = int(self.width * 0.46)
        y1 = int(self.height * 0.15)
        y2 = int(self.height * 0.35)

        self.centerPoint = [(x1 + x2) // 2, (y1 + y2) // 2]

    def filterDepth(self, frame, closestDistant, furthestDistant):
        return (np.where(((frame <= furthestDistant) & (frame >= closestDistant)), 128, 0)).astype(np.uint8)

    def enhanceFrame(self, frame):
        np.clip(frame, 0, 2 ** 10 - 1, frame)
        frame >>= 2
        return frame.astype(np.uint8)

    def getNeighbourhoodROI(self, frame, centerPoint, side):
        lowerHeight = centerPoint[1] - side // 2
        upperHeight = centerPoint[1] + side // 2
        lowerWidth = centerPoint[0] - side // 2
        upperWidth = centerPoint[0] + side // 2
        return frame[lowerHeight:upperHeight, lowerWidth:upperWidth]

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

    def initTracker(self, boundingBox):
        frame = self.cap.read()[1]
        frame = self.enhanceFrame(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center = self.getNeighbourhoodROI(gray, self.centerPoint, 40)
        filtered = self.filterFrame(frame, center)
        flood = self.floodFill(filtered)
        img, boundingBox = self.findHandContour(flood, drawContour=True)[0:4:3]
        #cv2_imshow(filtered)
        self.tracker.init(filtered, boundingBox)

    def trackHand(self):
        frameLoaded, frame = self.cap.read()
        if not frameLoaded:
            return None

        frame = self.enhanceFrame(frame)
        color = frame.copy()

        frame = self.filterDepth(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 10, 30)
        #cv2.imshow(frame)
        trackerUpdated, boundRect = self.tracker.update(frame)
        if trackerUpdated:
            # Tracking success
            p1 = (int(boundRect[0]), int(boundRect[1]))
            p2 = (int(boundRect[0] + boundRect[2]), int(boundRect[1] + boundRect[3]))
            cv2.rectangle(color, p1, p2, (255, 0, 0), 2, 1)
            cv2.circle(color, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2), 3, (0, 0, 255), -1)
            coords = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

        else:
            # Tracking failure
            cv2.putText(color, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),2)
            coords = None
        return coords


videoPath = "C:\\Users\\Damian\\Documents\\Studia\\PT\\Kinart\\videokinec_depth4_v2.avi"
hT = HandTracker(videoPath)

hT.initTracker(1)
hT.trackHand()