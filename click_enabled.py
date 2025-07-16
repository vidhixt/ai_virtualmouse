import cv2
import mediapipe as mp
import pyautogui
import math


# these 2 lines are added to make it smooth
prev_x, prev_y = 0, 0
smoothing = 7  # smaller = more smooth, larger = faster

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Get your screen size
screen_w, screen_h = pyautogui.size()

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # Flip so movement feels natural (like a mirror)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape

            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id == 8:
                    index_x, index_y = cx, cy
                    cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

                    # Convert webcam coordinates to screen coordinates
                    screen_x = int(lm.x * screen_w)
                    screen_y = int(lm.y * screen_h)

                    # Move mouse to this position
                    #pyautogui.moveTo(screen_x, screen_y)
                    
                    # Smooth the movement
                    curr_x = int(lm.x * screen_w)
                    curr_y = int(lm.y * screen_h)

                    smoothed_x = prev_x + (curr_x - prev_x) // smoothing
                    smoothed_y = prev_y + (curr_y - prev_y) // smoothing

                    pyautogui.moveTo(smoothed_x, smoothed_y)

                    prev_x, prev_y = smoothed_x, smoothed_y

                if id==4:
                    thumb_x, thumb_y = cx, cy
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            distance = math.hypot(thumb_x - index_x, thumb_y - index_y)

            # Click if distance is small (pinch)
            if distance < 40:  # adjust this threshold if needed
                pyautogui.click()
                cv2.putText(frame, "Click!", (index_x, index_y - 20),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

    cv2.imshow("Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
