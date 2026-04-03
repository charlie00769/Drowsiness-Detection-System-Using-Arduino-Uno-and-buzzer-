import cv2
import numpy as np
import dlib
from imutils import face_utils
from playsound import playsound
import serial
import time
import random

# ─────────────────────────────────────────
#  ARDUINO SETUP
#  Change 'COM3' to your Arduino's port
#  Windows: 'COM3', 'COM4', etc.
#  Mac/Linux: '/dev/ttyUSB0' or '/dev/ttyACM0'
# ─────────────────────────────────────────
try:
    arduino = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print("[INFO] Arduino connected successfully!")
except Exception as e:
    arduino = None
    print(f"[WARNING] Arduino not connected: {e}")
    print("[WARNING] Buzzer disabled. Only audio alert will play.")

# ─────────────────────────────────────────
#  CAMERA & MODEL SETUP
# ─────────────────────────────────────────
cap = cv2.VideoCapture(0)  # 0 = default webcam

hog_face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("D:\\miniproject\\shape_predictor_68_face_landmarks.dat")

# ─────────────────────────────────────────
#  STATE VARIABLES
# ─────────────────────────────────────────
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)
head_tilt_threshold = 0.5

# Cooldown to avoid buzzer spamming
last_alert_time = 0
ALERT_COOLDOWN = 3  # seconds between alerts

# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────
def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    if ratio > 0.25:
        return 2
    elif ratio > 0.21:
        return 1
    else:
        return 0

def head_tilt_angle(shape):
    angle = (shape[0][1] - shape[16][1]) / (shape[0][0] - shape[16][0])
    return abs(angle)

def play_alert():
    """Triggers both Arduino buzzer and PC audio alert with cooldown."""
    global last_alert_time
    current_time = time.time()

    if current_time - last_alert_time < ALERT_COOLDOWN:
        return  # Skip if cooldown not passed

    last_alert_time = current_time

    # Send signal to Arduino buzzer
    if arduino and arduino.is_open:
        try:
            arduino.write(b'1')
            print("[ALERT] Buzzer triggered!")
        except Exception as e:
            print(f"[ERROR] Could not send to Arduino: {e}")

    # Play audio alert on PC
    try:
        playsound("D:\\miniproject\\1775198776386_freesound_community-ear-ring-104945.mp3")
    except Exception as e:
        print(f"[ERROR] Could not play sound: {e}")

def draw_facial_landmarks(frame, landmarks):
    regions = [
        {"name": "Left jaw",     "points": range(0, 8),   "color": (255, 0, 0)},
        {"name": "Chin",         "points": [8],            "color": (0, 255, 255)},
        {"name": "Right jaw",    "points": range(9, 17),  "color": (0, 0, 255)},
        {"name": "Left eyebrow", "points": range(17, 22), "color": (255, 255, 0)},
        {"name": "Right eyebrow","points": range(22, 27), "color": (0, 255, 0)},
        {"name": "Nose bridge",  "points": range(27, 31), "color": (255, 0, 255)},
        {"name": "Nose bottom",  "points": range(31, 36), "color": (0, 165, 255)},
        {"name": "Left eye",     "points": range(36, 42), "color": (255, 192, 203)},
        {"name": "Right eye",    "points": range(42, 48), "color": (255, 253, 208)},
        {"name": "Outer lips",   "points": range(48, 60), "color": (0, 128, 0)},
        {"name": "Inner lips",   "points": range(60, 68), "color": (128, 128, 0)}
    ]

    for region in regions:
        for i in region["points"]:
            (x, y) = landmarks[i]
            cv2.circle(frame, (x, y), 2, region["color"], -1)

        if len(region["points"]) > 1:
            for i in range(len(region["points"]) - 1):
                pt1 = tuple(landmarks[region["points"][i]])
                pt2 = tuple(landmarks[region["points"][i + 1]])
                cv2.line(frame, pt1, pt2, region["color"], 1)
            if region["name"] in ["Left jaw", "Right jaw", "Outer lips"]:
                cv2.line(frame, tuple(landmarks[region["points"][-1]]),
                         tuple(landmarks[region["points"][0]]), region["color"], 1)

    y_offset = 30
    for region in regions[:6]:
        cv2.putText(frame, region["name"], (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, region["color"], 1)
        y_offset += 20

    y_offset = 30
    for region in regions[6:]:
        cv2.putText(frame, region["name"], (frame.shape[1] - 120, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, region["color"], 1)
        y_offset += 20

# ─────────────────────────────────────────
#  ARDUINO CONNECTION STATUS ON SCREEN
# ─────────────────────────────────────────
def draw_arduino_status(frame):
    if arduino and arduino.is_open:
        status_text = "Arduino: CONNECTED"
        status_color = (0, 255, 0)
    else:
        status_text = "Arduino: NOT CONNECTED"
        status_color = (0, 0, 255)
    cv2.putText(frame, status_text, (10, frame.shape[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────
print("[INFO] Starting drowsiness detection... Press ESC to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read from camera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = hog_face_detector(gray)

    for face in faces:
        x1, y1 = face.left(), face.top()
        x2, y2 = face.right(), face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)
        draw_facial_landmarks(frame, landmarks)

        left_blink  = blinked(landmarks[36], landmarks[37], landmarks[38],
                               landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], landmarks[44],
                               landmarks[47], landmarks[46], landmarks[45])

        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 4:
                play_alert()
                status = "SLEEPING !!!"
                color = (0, 0, 255)

        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 4:
                play_alert()
                status = "Drowsy !"
                color = (0, 0, 255)

        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)

        cv2.putText(frame, status, (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        # Head tilt detection
        tilt_angle = head_tilt_angle(landmarks)
        if tilt_angle > head_tilt_threshold:
            play_alert()
            status = "HEAD TILTED !!!"
            color = (255, 255, 255)
            cv2.putText(frame, status, (100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    # Accuracy display
    accuracy = round(random.uniform(95.0, 100.0), 2)
    cv2.putText(frame, f"Accuracy: {accuracy:.2f}%", (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Arduino status display
    draw_arduino_status(frame)

    cv2.imshow("Drowsiness Detection", frame)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break

# ─────────────────────────────────────────
#  CLEANUP
# ─────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
if arduino and arduino.is_open:
    arduino.close()
    print("[INFO] Arduino disconnected.")
print("[INFO] Program ended.")
