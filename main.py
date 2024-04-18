
from flask import Flask, render_template, request, jsonify, Response
import cv2
import tensorflow as tf
import numpy as np
import mediapipe as mp
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import serial
import time
import math
#time.sleep(2) 
#import gsm

#import readarduino


# class SerialProxy:
#     def __init__(self):
#         self.__serial = None

#     def serial_function(self):
#         if self.__serial is None:
#             self.__serial = serial.Serial('COM3', 9600,timeout=2)
#         reply = self.__serial.readline().decode().strip()
#         return reply
# ss=SerialProxy()
ser = serial.Serial('COM3', baudrate=9600, timeout=1)
ser1 = serial.Serial('COM5', baudrate=9600, timeout=1)
data=ser.readline().decode().strip()
print(data)
while data == '':
    data=ser.readline().decode().strip()
    print(data)
ref=float(data)

app = Flask(__name__)
dat=[]
global letter
global word
global sentence
global flag

flag=0
bot_data={"hospital":"Nearest hospital is SK hospital which is 300m from the first right",
          "emergency contact":"In case of any emergency please contact '108'",
          "normal heart rate":"60 to 100 beats per minute",
          "cardiac arrest":"loss of response,no normal breathing,loss of pulse,chest pain",
          "normal temperature":"36.1 to 37.2 degree celsius"}

letter=""
word=""
sentence=""

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    return distance

def detect_hand_gestures(frame, hand_landmarks,mp_hands,mp_drawing):
    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_finger = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_finger = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    index_finger_m = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_finger_m = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_finger_m = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_finger_m = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    index_t_x, index_t_y = int(index_finger.x * frame.shape[1]), int(index_finger.y * frame.shape[0])
    middle_t_x, middle_t_y = int(middle_finger.x * frame.shape[1]), int(middle_finger.y * frame.shape[0])
    ring_t_x, ring_t_y = int(ring_finger.x * frame.shape[1]), int(ring_finger.y * frame.shape[0])
    pinky_t_x, pinky_t_y = int(pinky_finger.x * frame.shape[1]), int(pinky_finger.y * frame.shape[0])
    
    index_m_x, index_m_y = int(index_finger_m.x * frame.shape[1]), int(index_finger_m.y * frame.shape[0])
    middle_m_x, middle_m_y = int(middle_finger_m.x * frame.shape[1]), int(middle_finger_m.y * frame.shape[0])
    ring_m_x, ring_m_y = int(ring_finger_m.x * frame.shape[1]), int(ring_finger_m.y * frame.shape[0])
    pinky_m_x, pinky_m_y = int(pinky_finger_m.x * frame.shape[1]), int(pinky_finger_m.y * frame.shape[0])
    
    wrist_x,wrist_y = int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0])

    d_ref=calculate_distance((index_t_x, index_t_y),(wrist_x,wrist_y))
    d=calculate_distance((index_t_x, index_t_y),(middle_t_x, middle_t_y))/d_ref
    d1=calculate_distance((index_t_x, index_t_y),(index_m_x, index_m_y))/d_ref
    d2=calculate_distance((middle_t_x, middle_t_y),(middle_m_x, middle_m_y))/d_ref
    d3=calculate_distance((ring_t_x, ring_t_y),(ring_m_x, ring_m_y))/d_ref
    d4=calculate_distance((pinky_t_x, pinky_t_y),(pinky_m_x, pinky_m_y))/d_ref
    
    
    if d1>0.25 and d2>0.25 and d3<0.4 and d4<0.4 and d>0.1:
        label="Peace"
        
    elif d1>0.25 and d2>0.25 and d3>0.25 and d4>0.25:
        label="Hand"
        
    else:
        label="No Gesture"
    return label



def mail():
    subject = "Alert"
    body = "parent needs your help....."
    sender_email = "elderlycaredl@gmail.com"
    receiver_email = "sreelakshmias214@gmail.com"
    password = "famn irwk yenz efok"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/video_call')
def video_call():
    return render_template('index.html')

def process_frames():
    global letter
    global word
    global sentence

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    count=0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_hand_gestures(frame, hand_landmarks,mp_hands,mp_drawing)
                #print(gesture)
                sentence=gesture
                if gesture=="Peace":
                    count+=1
                else:
                    count=0

                #cv2.putText(frame, f"Gesture: {gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if count>20:
                    count=0
                    mail()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n\r\n' + letter.encode() + b'\r\n\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(process_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/fetch_data')
def fetch_data():
    global letter
    global word
    global sentence
    global flag
    data = ser.readline().decode().strip()
    if data != "":
        try:
            loaded_model=pickle,load("eeg_4class.pickel")
            if len(dat<148):
                dat.append(data)
            else:
                dat.pop(0)
                d=np.array(dat)
                y=loaded_model.predict(d)
                if y!=0:
                    flag=1
                    ser1.write(b'AT\r')
                    rcv = ser1.read(10)
                    print(rcv)
                    time.sleep(1)
                    ser1.write(b'ATD9995234163;\r')
                    print('Calling…')
                    time.sleep(30)
                    ser1.write(b'ATH\r')
                    print('Hang Call…')
        except:
            data=float(data)
            word=str(data-10)
            letter=str(2*float(word))
            if ref-data>0.4 and flag==0:
                flag=1
                ser1.write(b'AT\r')
                rcv = ser1.read(10)
                print(rcv)
                time.sleep(1)
                ser1.write(b'ATD6238167627;\r')
                print('Calling…')
                time.sleep(30)
                ser1.write(b'ATH\r')
                print('Hang Call…')

    data = {'letter': letter, 'word': word, 'sentence':sentence}
    return jsonify(data)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    return render_template('bot.html')

@app.route("/get")
def get_bot_response():
    userText = str(request.args.get('msg'))
    print(bot_data)
    for i in bot_data:
        print(i)
        if i in userText:
            return bot_data[i] 
    return "Sorry could not understand"

if __name__ == '__main__':
    app.run(debug=False)
