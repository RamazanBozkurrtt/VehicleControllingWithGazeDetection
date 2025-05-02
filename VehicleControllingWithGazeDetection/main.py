import socket
import time
import keyboard
import cv2
import dlib
import numpy as np
from imutils import face_utils
from collections import deque
import tkinter as tk
from threading import Thread


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('C:/GazeControlledVehicle/shape_predictor_68_face_landmarks.dat')
pupil_positions = deque(maxlen=5)
running = False
ESP32_IP = "192.168.4.1"  # ESP32'nin varsayılan AP IP adresi
PORT = 5000
current_direction = ""

def send_command(cmd):
   try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)  # Bağlantı timeout'u
            s.connect((ESP32_IP, PORT))
            s.sendall(cmd.encode())
   except Exception as e:
        print(f"Error sending command: {e}")

def detect_pupil(eye_region, frame_color, draw=True):
    blurred = cv2.GaussianBlur(eye_region, (7, 7), 0)
    _, threshold_eye = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) < 20:
            return None
        (cx, cy), _ = cv2.minEnclosingCircle(max_contour)
        pupil_x = int(cx)
        pupil_y = int(cy)
        if draw:
            cv2.circle(frame_color, (pupil_x, pupil_y), 2, (0, 0, 255), -1)
        return (pupil_x, pupil_y)
    return None

def start_tracking():
    global running, current_direction
    running = True
    cap = cv2.VideoCapture(0)

    #key_states = {'w': False, 'a': False, 's': False, 'd': False}

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        direction = ""

        for face in faces:
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            left_eye = shape[42:48]
            right_eye = shape[36:42]

            cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)

            (lx, ly, lw, lh) = cv2.boundingRect(left_eye)
            (rx, ry, rw, rh) = cv2.boundingRect(right_eye)
            pad = 5

            # Sol göz
            left_roi = gray[ly-pad:ly+lh+pad, lx-pad:lx+lw+pad]
            left_color = frame[ly-pad:ly+lh+pad, lx-pad:lx+lw+pad]
            pupil = detect_pupil(left_roi, left_color)

            if pupil:
                pupil_positions.append(pupil)

            # Sağ göz
            right_roi = gray[ry-pad:ry+rh+pad, rx-pad:rx+rw+pad]
            right_color = frame[ry-pad:ry+rh+pad, rx-pad:rx+rw+pad]
            detect_pupil(right_roi, right_color)

            if len(pupil_positions) == pupil_positions.maxlen:
                avg_x = sum(pos[0] for pos in pupil_positions) / pupil_positions.maxlen
                avg_y = sum(pos[1] for pos in pupil_positions) / pupil_positions.maxlen

                if avg_x < lw * 0.3:
                    direction = "Sola dön"
                    send_command('A')
                elif avg_x > lw * 0.7:
                    direction = "Sağa dön"
                    send_command('D')
                elif avg_y < lh * 0.3:
                    direction = "İleri git"
                    send_command('W')
                elif avg_y > lh * 0.7:
                    direction = "Geri git"
                    send_command('S')
                else:
                    direction = "Dur"
                    send_command('O')

        if direction:
            current_direction = direction
            direction_label.config(text="Yön: " + current_direction)

        cv2.imshow("Göz Takip", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def stop_tracking():
    global running
    running = False

# --- Tkinter GUI ---
window = tk.Tk()
window.title("Göz Takip Arayüzü")
window.geometry("300x150")

start_button = tk.Button(window, text="Başlat", command=lambda: Thread(target=start_tracking).start(), font=("Arial", 12))
start_button.pack(pady=10)

stop_button = tk.Button(window, text="Durdur", command=stop_tracking, font=("Arial", 12))
stop_button.pack(pady=10)

direction_label = tk.Label(window, text="Yön: ---", font=("Arial", 12))
direction_label.pack(pady=10)

window.mainloop()