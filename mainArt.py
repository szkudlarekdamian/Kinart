from handTracker import *
import config
import globals
import GUI
import kinect_video_recorder as kin
import numpy as np
import cv2

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
                frameWithCoords, coords = hT.trackHand(frame)
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