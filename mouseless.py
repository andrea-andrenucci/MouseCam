import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import pyautogui
import numpy as np
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

# Initialize Tkinter root window
root = tk.Tk()
root.withdraw()

# Function to get the camera index from the user using a tkinter dialog
def get_camera_index():
    camera = simpledialog.askinteger("Camera Selection", "Enter the camera index (integer):")
    return camera

# Choose the camera to use
camera = get_camera_index()

# Attempt to open the selected camera
cam = cv2.VideoCapture(camera)
if not cam.isOpened(): 
    cam.release()
    # If the selected camera couldn't be opened, try using the default camera (index 0)
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        messagebox.showerror("Camera Error", "Please connect a webcam before using.")
        exit()


#Initialize hand detector
detector = HandDetector(detectionCon=0.9, maxHands=1, minTrackCon=0.8)
cam_w, cam_h = 640, 480
screen_w, screen_h = pyautogui.size()


l_delay = 0
hold=0
l_clk_event = threading.Event()

#* PARAMETERS *#

#* Offset parameters
offset_hand_center = 100
offset_w_start = 250
offset_h_start = 200
offset_w_end = 150
offset_h_end = 100

#* filters and trasholds
filter_x=0
filter_y=0
filter_treshold=10
pnk_treshold = 35
ind_treshold = 1100
mid_treshold = 1000

status = True;
show_menu=False;

cam.set(3, cam_w)
cam.set(4, cam_h)

def l_clk_delay():
    global l_delay
    time.sleep(1)
    l_delay = 0
    l_clk_event.set()

# Absolute distance
def distance(x_0, x_1, y_0, y_1):
    return int(abs(x_0-x_1)**2 + abs(y_0-y_1)**2)

#? -------------------------------------------------------------------------------

def create_option_window():
        # Create a window to display the sliders
        cv2.namedWindow("Parameters")
        # Set the size of the "Parameters" window
        window_width, window_height = 800, 400
        cv2.resizeWindow("Parameters", window_width, window_height)

        # Create trackbars for each parameter
        cv2.createTrackbar("Hand Off", "Parameters", offset_hand_center, 200, update_parameters)
        cv2.createTrackbar("W St Off", "Parameters", offset_w_start, 300, update_parameters)
        cv2.createTrackbar("H St Off", "Parameters", offset_h_start, 300, update_parameters)
        cv2.createTrackbar("W End Off", "Parameters", offset_w_end, 300, update_parameters)
        cv2.createTrackbar("H End Off", "Parameters", offset_h_end, 300, update_parameters)
        cv2.createTrackbar("Filter X", "Parameters", filter_x, 1920, update_parameters)
        cv2.createTrackbar("Filter Y", "Parameters", filter_y, 1080, update_parameters)
        cv2.createTrackbar("Filter Trsh", "Parameters", filter_treshold, 100, update_parameters)
        cv2.createTrackbar("Pnk Trsh", "Parameters", pnk_treshold, 100, update_parameters)
        cv2.createTrackbar("Ind Trsh", "Parameters", ind_treshold, 2000, update_parameters)
        cv2.createTrackbar("Mid Trsh", "Parameters", mid_treshold, 2000, update_parameters)



# Function to update parameters based on trackbar positions
def update_parameters(*args):
    global offset_hand_center, offset_w_start, offset_h_start, offset_w_end, offset_h_end, \
           filter_x, filter_y, filter_treshold, pnk_treshold, ind_treshold, mid_treshold
    offset_hand_center = cv2.getTrackbarPos("Hand Off", "Parameters")
    offset_w_start = cv2.getTrackbarPos("W St Off", "Parameters")
    offset_h_start = cv2.getTrackbarPos("H St Off", "Parameters")
    offset_w_end = cv2.getTrackbarPos("W End Off", "Parameters")
    offset_h_end = cv2.getTrackbarPos("H End Off", "Parameters")
    filter_x = cv2.getTrackbarPos("Filter X", "Parameters")
    filter_y = cv2.getTrackbarPos("Filter Y", "Parameters")
    filter_treshold = cv2.getTrackbarPos("Filter Trsh", "Parameters")
    pnk_treshold = cv2.getTrackbarPos("Pnk Trsh", "Parameters")
    ind_treshold = cv2.getTrackbarPos("Ind Trsh", "Parameters")
    mid_treshold = cv2.getTrackbarPos("Mid Trsh", "Parameters")



while True:
    success, img = cam.read()
    img = cv2.flip(img, 1)
    img = cv2.flip(img, 0)

    color = (0, 250, 0) if status else (0, 0, 250)

    hands, img = detector.findHands(img, flipType=False)

    # Area utile    
    cv2.rectangle(
        img,
        (offset_w_start, offset_h_start),
        (cam_w - offset_w_end, cam_h - offset_h_end),
        color,
        2
    )

    if hands:
        lmlist = hands[0]['lmList']

        #Cursore
        hnd_x, hnd_y = lmlist[0][0], lmlist[0][1] - offset_hand_center

        #Dita
        ind_tip_x, ind_tip_y = lmlist[8][0], lmlist[8][1]
        ind_btm_x, ind_btm_y = lmlist[6][0], lmlist[6][1]
        
        mid_tip_x, mid_tip_y = lmlist[12][0], lmlist[12][1]
        mid_btm_x, mid_btm_y = lmlist[10][0], lmlist[10][1]
        
        pnk_tip_x, pnk_tip_y = lmlist[20][0], lmlist[20][1]
        pnk_btm_x, pnk_btm_y = lmlist[18][0], lmlist[18][1]


        ind_distance = distance(ind_tip_x, ind_btm_x, ind_tip_y, ind_btm_y)
        mid_distance = distance(mid_tip_x, mid_btm_x, mid_tip_y, mid_btm_y)



        cv2.circle(img, (hnd_x, hnd_y), 5, (0, 255, 255), 2)
        fingers = detector.fingersUp(hands[0])

        if status:

            if fingers[1] == 1 and fingers[2] == 1:
                conv_x = int(np.interp(hnd_x, (offset_w_start, cam_w - offset_w_end), (0, screen_w)))
                conv_y = int(np.interp(hnd_y, (offset_h_start, cam_h - offset_h_end), (0, screen_h)))

                


                if filter_x==0 or filter_y==0:
                    filter_x=conv_x
                    filter_y=conv_y


                if abs(conv_x-filter_x) > filter_treshold or abs(conv_y-filter_y) > filter_treshold:
                    mouse.move(conv_x, conv_y)
                    filter_x=conv_x
                    filter_y=conv_y

            #* hold
            if abs(pnk_tip_y-pnk_btm_y) < pnk_treshold:
                if hold == 0:
                    hold=1
                    mouse.hold()
            else:
                if hold == 1:
                    hold=0
                    mouse.release()

            #* other ops
            if fingers[0] == 1 and ind_distance < ind_treshold and fingers[2] == 1:
                if l_delay == 0:
                    mouse.click(button="left")
                    l_delay = 1
                    l_clk_event.clear()
                    threading.Thread(target=l_clk_delay).start()
                else:
                    l_clk_event.wait()  # Attendere il completamento del thread precedente
            elif fingers[0] == 1 and fingers[1] == 1 and mid_distance < mid_treshold:
                if l_delay == 0:
                    mouse.click(button="right")
                    l_delay = 1
                    l_clk_event.clear()
                    threading.Thread(target=l_clk_delay).start()
                else:
                    l_clk_event.wait()  # Attendere il completamento del thread precedente
            elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0:
                if l_delay == 0:
                    mouse.click(button="left")
                    mouse.click(button="left")
                    l_delay = 1
                    l_clk_event.clear()
                    threading.Thread(target=l_clk_delay).start()
                else:
                    l_clk_event.wait()  # Attendere il completamento del thread precedente
            elif fingers[0] == 0 and fingers[1] == 0:
                if fingers[2] == 1:
                    mouse.wheel(delta=1)
                else:
                    mouse.wheel(delta=-1)

        #* Temporary stop
        if fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            if l_delay == 0:
                    status = not status
                    l_delay = 1
                    l_clk_event.clear()
                    threading.Thread(target=l_clk_delay).start()

    # Display the menu when 'o' key is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('o'):
        if not show_menu:
            create_option_window()

        else:
            cv2.destroyWindow("Parameters")
            
        show_menu = not show_menu

    # Show the image and process other events
    cv2.imshow("Camera Feed", img)

    # Break the loop when 'q' is pressed
    if key == ord('q'):
        break

# Release the webcam and destroy all windows
cam.release()
cv2.destroyAllWindows()
