import time
import cv2

from handTracker import HandTracker
import kinect_video_recorder as kin


if __name__ == "__main__":
    print('START')

    #Ścieżka do filmu z mapą głębi lub ID kamery
    videoPath = "../filmy_dla_Danona/videokinec_depth4_v2.avi"

    #Obiekt klasy HandTracker, której głównym zadaniem jest zwracanie współrzędnych dłoni, na podstawie filmu mapy głębi
    hT = HandTracker(videoPath)

    # frame = kin.get_depth_with_3rd_layer()

    start = time.time()
    print(start)

    while(hT.kinectOpened()):
        #Sztuczne spowolnienie klatek, tylko do celów testowych
        # time.sleep(0.1)

        #Pobieranie kolejnej klatki
        frame = kin.get_depth_with_3rd_layer()

        #Jeśli klatka została wczytana poprawnie to kontynuuj
        if frame is not None:
            #Jeśli dłoń nie została jeszcze zainicjalizowana do systemu
            if hT.handInitialized is False:

                pic = hT.getFrameWithInitBox(frame)
                #Pokaż klatkę z narysowaną przestrzenią na dłoń
                cv2.imshow('Kinart', pic)
                cv2.waitKey(1)
                #Jeśli wciśnięto 'z' to rozpocznij inicjalizację dłoni
                # if cv2.waitKey(1) == ord('z'):
                
                if time.time() - start > 15:
                    hT.initTracker(frame)
                    hT.handInitialized = True
            #Jeśli dłoń została zainicjalizowana to
            else:
                #Śledź dłoń i uzyskaj jej współrzędne
                frameWithCoords, coords = hT.trackHand(frame)
                cv2.imshow('Kinart', frameWithCoords)
                cv2.waitKey(1)
                
        else:
            break

    cv2.destroyAllWindows()        