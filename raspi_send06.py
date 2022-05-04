import cv2
import threading
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import time

from Module import sock_cli, temper
import os

#running = False
#running = True
r_flag = '0'
mjpg_PATH = "http://192.168.0.13:8091/?action=stream"

server_ip = "192.168.0.23"
server_port = 59010
cli = sock_cli.ClientSocket(server_ip, server_port)
a = temper.Gpio_set()

option = '-s 180 -p 50 -a 200 -v ko+f5'
msg = ( '체온을 측정 합니다.',
        '정상 입니다.',
        '다시 측정하세요.',
        '미등록 상태 입니다.',
        '삐이이 .')

def speak(option, msg) :
    os.system("espeak {} '{}'".format(option,msg))

def show_video():
    #global running
    #cap = cv2.VideoCapture(-1)
    cap = cv2.VideoCapture(mjpg_PATH)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    label1.resize(width, height)
    #while running:
    while True:
        ret, img = cap.read()
        #img = cv2.flip(img, -1)
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
            h,w,c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            label1.setPixmap(pixmap)
        else:
            QtWidgets.QMessageBox.about(win, "Error", "Cannot read frame.")
            print("cannot read frame.")
            break
    cap.release()
    print("Thread end.")

def show_text():
    #global running
    global r_flag
    label2.resize(300,200)
    #while running:
    while True:
        if r_flag == '0':
            label2.setText("36.5도 입니다.")
            label2.setStyleSheet("color: red;"
                         "border-style: solid;"
                         "border-width: 5px;"
                         "border-color: #FA8072;"
                         "border-radius: 5px")
            #print("flag= ", r_flag)    
        else:
            print("flag= ", r_flag)
        time.sleep(0.3)
        
"""        for i in range(1,101):
            if i < 30:  
                label2.setText("기다려주세요")
                label2.setStyleSheet("color: red;"
                             "border-style: solid;"
                             "border-width: 5px;"
                             "border-color: #FA8072;"
                             "border-radius: 5px")
            elif i < 70:   
                label2.setText("시작합니다")
                label2.setStyleSheet("color: green;"
                             "border-style: solid;"
                             "border-width: 5px;"
                             "border-color: #7FFFD4;"
                             "border-radius: 5px")
            elif i < 98:   
                label2.setText("종료됩니다.\n 띄어쓰기했음")
                label2.setStyleSheet("color: blue;"
                             "border-style: solid;"
                             "border-width: 5px;"
                             "border-color: #1E90FF;"
                             "border-radius: 5px")
            else:
                i = 0
            time.sleep(0.03)
"""
def check_temp():
    #global running
    #global r_flag
    global cli
    global msg
    label2.resize(300,200)
    temp = '0'
    #while running:
    while True:
        sign = cli.recmessage()
        #sign = '0'
        #r_flag = sign
        
        #print("sign= ",sign)
        
        if '0' in sign:
            label2.setText("체온을 측정합니다. 잠시만 기다려주세요.   측정온도: " + temp)
            label2.setStyleSheet("color: red;"
                         "border-style: solid;"
                         "border-width: 5px;"
                         "border-color: #FA8072;"
                         "border-radius: 5px")
            
            speak(option,msg[0])
            tot_temp = 0.0
            for i in range(3):
                #dis = a.distance()
                temper = a.get_temp()
                tot_temp += temper
            temper = round(tot_temp / 3.0, 2)    
            temp = str(temper)
            cli.sendtemp(temp)
            
            #print(temp)
            print("온도 보냄   " + temp)
            
        elif '1' in sign:
            label2.setText("등록자 / 온도정상")
            label2.setStyleSheet("color: green;"
                        "border-style: solid;"
                        "border-width: 5px;"
                        "border-color: #7FFFD4;"
                        "border-radius: 5px")
            print("등록자 / 온도정상")
            speak(option,msg[1])
            
        elif '2' in sign:
            label2.setText("등록자 / 온도이상")
            label2.setStyleSheet("color: blue;"
                        "border-style: solid;"
                        "border-width: 5px;"
                        "border-color: #1E90FF;"
                        "border-radius: 5px")
            print("등록자 / 온도이상")
            speak(option,msg[2])
            
        elif '3' in sign:
            label2.setText("미등록자 / 온도정상")
            label2.setStyleSheet("color: blue;"
                        "border-style: solid;"
                        "border-width: 5px;"
                        "border-color: #1E90FF;"
                        "border-radius: 5px")
            print("미등록자 / 온도정상")
            speak(option,msg[3])
            
        elif '4' in sign:
            label2.setText("미등록자 / 온도이상")
            label2.setStyleSheet("color: blue;"
                        "border-style: solid;"
                        "border-width: 5px;"
                        "border-color: #1E90FF;"
                        "border-radius: 5px")
            print("미등록자 / 온도이상")
            speak(option,msg[4])
            
        else:
            pass

        #print("36.5도 정상입니다.")
        time.sleep(0.1)
    
def stop():
    global running
    running = False
    print("stoped..")

def start():
    global running
    running = True
    th1 = threading.Thread(target=show_video)
    #th2 = threading.Thread(target=show_text)
    th3 = threading.Thread(target=check_temp)
    th1.start()
    #th2.start()
    th3.start()
    print("started..")

def onExit():
    print("exit")
    stop()

app = QtWidgets.QApplication([])
win = QtWidgets.QWidget()
vbox = QtWidgets.QVBoxLayout()
label1 = QtWidgets.QLabel()
label2 = QtWidgets.QLabel()
#btn_start = QtWidgets.QPushButton("Start")
#btn_stop = QtWidgets.QPushButton("Stop")
vbox.addWidget(label1)
vbox.addWidget(label2)
#vbox.addWidget(btn_start)
#vbox.addWidget(btn_stop)
win.setLayout(vbox)
win.setWindowTitle('e List')
win.show()

#btn_start.clicked.connect(start)
#btn_stop.clicked.connect(stop)
#app.aboutToQuit.connect(onExit)

th1 = threading.Thread(target=show_video)
#th2 = threading.Thread(target=show_text)
th3 = threading.Thread(target=check_temp)
th1.start()
#th2.start()
th3.start()

sys.exit(app.exec_())