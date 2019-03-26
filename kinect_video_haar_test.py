#import the necessary modules
import freenect
import cv2
import numpy as np

#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array

#function to get depth image from kinect in 2 dimensions (heigth, width)
def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array

#function to get depth image from kinect in 3 dimensions (heigth, width, layers)
def get_depth_with_3rd_layer():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    array = cv2.cvtColor(array, cv2.COLOR_GRAY2RGB)
    return array

#function to get both rgb and depth image
def get_colour_and_dept_frame():
    colour_frame = get_video()
    depth_frame = get_depth_with_3rd_layer()
    return colour_frame, colour_frame

def create_depth_and_colour_recordings(colour_video_name, depth_video_name):
    depth_with_3_dimensions = get_depth_with_3rd_layer()
    height, width, layers =  depth_with_3_dimensions.shape

    video_colour = cv2.VideoWriter(colour_video_name,
                                    cv2.VideoWriter_fourcc(*"MPNG"),
                                    10,
                                    (width, height))
    video_depth = cv2.VideoWriter(depth_video_name,
                                    cv2.VideoWriter_fourcc(*"MPNG"),
                                    10,
                                    (width, height))

    return video_colour, video_depth


if __name__ == "__main__":
    colour_video_name = 'videokinec_colour0.avi'
    depth_video_name = 'videokinec_depth0.avi'

    video_colour, video_depth = create_depth_and_colour_recordings(colour_video_name,
                                                                    depth_video_name)

    print('Creating files for videos:', colour_video_name, ' and ', depth_video_name)

    haar_palm_file = 'Haarcascades/fist.xml'

    hand_cascade = cv2.CascadeClassifier(haar_palm_file)

    while 1:
        #get a frame from RGB camera
        colour_frame = get_video()
        #get a frame from depth sensor
        depth_frame = get_depth_with_3rd_layer()
        #display RGB image
        #cv2.imshow('RGB image', colour_frame)
        #display depth image
        #cv2.imshow('Depth image', depth_frame)

        rgb2gray_frame = cv2.cvtColor(colour_frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('RGB image', rgb2gray_frame)

        # depth_frame = get_depth_with_3rd_layer()
        # ret,thresh1 = cv2.threshold(depth_frame,127,255,cv2.THRESH_BINARY)

        hands = hand_cascade.detectMultiScale(rgb2gray_frame, 1.1, 5)
        for (x, y, w, h) in hands:
            rgb2gray_frame = cv2.rectangle(rgb2gray_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Display the result of our processing
        cv2.imshow('result', rgb2gray_frame)        

        #write colour and depth frames to videos
        video_colour.write(colour_frame)
        video_depth.write(depth_frame)

        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()

    video_colour.release()
    print('Colour video saved as:', colour_video_name)
    video_depth.release()
    print('Depth video saved as:', depth_video_name)