<div align="center">

# 🚗 Drowsiness Detection System with Arduino Alert

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg?logo=opencv)](https://opencv.org/)
[![Arduino](https://img.shields.io/badge/Arduino-Compatible-00979D.svg?logo=arduino)](https://www.arduino.cc/)

A highly precise, real-time Computer Vision system designed to detect driver drowsiness and fatigue. By monitoring eye closures and head posture via a webcam, the system triggers a **fail-safe dual-alert system**: a local computer audio warning combined with a blaring hardware buzzer activated via serial communication to an Arduino.

----

</div>

## ✨ Key Features & Capabilities

* [cite_start]**Comprehensive Facial Mapping:** Maps 68 facial landmarks in real-time and categorizes them into 11 distinct, color-coded regions on the UI (e.g., Left/Right Jaw, Eyes, Lips, Nose Bridge).
* [cite_start]**Eye Aspect Ratio (EAR) Analysis:** Precisely calculates the ratio of the eyes to distinguish between normal blinks, extended drowsiness (warning state), and sleep (critical state).
* [cite_start]**Postural Head Tilt Detection:** Monitors the slope of the jawline to alert the user if their head drops or tilts significantly (configurable threshold set to 0.5).
* **Synchronized Dual-Alert System:**
  * [cite_start]**PC Audio:** Plays a high-pitched MP3 ringtone directly from the computer.
  * [cite_start]**Hardware Buzzer:** Communicates with an Arduino at a 9600 baud rate to activate a physical 5V buzzer for 1.5 seconds[cite: 1, 2].
* [cite_start]**Smart Cooldown Mechanism:** Both alarms share a 3-second cooldown timer to prevent the alarms from rapid-firing, overlapping, or crashing the serial port.

---

## 🧮 Mathematical Logic (How it Works)

The software relies on two primary geometric calculations derived from the `shape_predictor_68_face_landmarks.dat` model.

### 1. Eye Aspect Ratio (EAR) for Blinking
To detect if an eye is closed, the system calculates the Euclidean distance between the vertical eye landmarks and divides it by the horizontal eye landmarks. The formula used is:

$$EAR = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 ||p_1 - p_4||}$$

Where $p_1, ..., p_6$ are the 2D landmark locations for a given eye. [cite_start]If this ratio drops below `0.25`, it registers as a blink or closure. [cite_start]Continuous closures across consecutive frames trigger the "Drowsy!" or "SLEEPING !!!" states.

### 2. Head Tilt Calculation
[cite_start]The system calculates the slope of the driver's face by comparing the leftmost jaw point (landmark 0) and the rightmost jaw point (landmark 16). The absolute angle slope is calculated as:

$$Tilt = \left| \frac{y_0 - y_{16}}{x_0 - x_{16}} \right|$$

[cite_start]If the resulting value exceeds the threshold of `0.5`, the "HEAD TILTED !!!" alert is triggered.

---

## 🛠️ Hardware Setup & Wiring

* Standard PC Webcam
* Arduino Uno (or similar compatible board)
* 5V Active Buzzer
* Jumper Wires

### 🔌 Arduino Wiring Guide

| Component | Arduino Pin | Description |
| :--- | :--- | :--- |
| **Buzzer Positive (+)** | Digital Pin 8 | [cite_start]Receives the `HIGH` voltage to make sound. |
| **Buzzer Negative (-)** | GND | Connects to ground to complete the circuit. |

---

## 💻 Software & Library Requirements

**Environment:** Python 3.x, Arduino IDE

Install all required Python dependencies via your terminal:
```bash
pip install opencv-python numpy dlib imutils playsound pyserial
