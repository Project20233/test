from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, QDate, QTime,QTimer,Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5 import QtGui
from datetime import datetime
from datetime import datetime
##Lora
import socket
import firebase_admin
from firebase_admin import db, credentials, storage
import time



def getData(data):
    global battery, temp, hum,listS

    data = str(data)
    data = data[2:]
    data = data.split(';')
    data = data[0]
    data = data.split(':')
    idMachine = data[0]
    data = data[1]
    # print(len(data))
    for i in range(0, len(listS)):
        if idMachine == listS[i]['idMachine']:
            print(idMachine)
            type = listS[i]['typeMachine']
            if type == "PM":
                print(idMachine)
                ##Baterry
                baterryPM = int(data[16:20], 16)/1000
                print("Baterry: ", baterryPM)
                ##PM 2.5
                PM25 = int(data[22:26], 16)
                print("PM 2.5: ", PM25, data[22:26])
                ##PM 10
                PM10 = int(data[26:30], 16)
                print("PM 10: ", PM10, data[26:30])
                ##PM 10
                PM1 = int(data[30:34], 16)
                print("PM 1: ", PM1, data[30:34])
                timeCycle = time.time()
                data = {
                    "idMachine": idMachine,
                    "type": "PM",
                    "timecycle": int(timeCycle),
                    "Baterry": float(baterryPM),
                    "PM25": float(PM25),
                    "PM10": float(PM10),
                    "PM1": float(PM1),
                }
                dt_string = "idMachine: "+idMachine+"\nBattery: "+str(baterryPM) +"\nPM 2.5: "+str(PM25)+"\nPM 10: "+str(PM10)+"\nPM 1: "+str(PM1)
                dlg.label_2.setText(str(dt_string))
                try:
                    db.reference("/SensorHistory").push().set(data)

                except Exception as er:
                    e = er
                    print("Internet Problem")

            elif type == "TempHum_LHT52":
                ##Baterry
                if len(data) == 32:
                    # print(idMachine)

                    battery = int(data[26:30], 16) / 1000
                    print("Baterry: ", battery, " V")
                ## Temp and Hum
                if len(data) == 40:
                    temp = int(data[16:20], 16) / 100
                    hum = int(data[20:24], 16) / 10
                    print("Temperture: ", temp, " C", " Humdity: ", hum, " %")
                    timeCycle = time.time()
                    data = {
                        "idMachine": idMachine,
                        "type": "TempHum",
                        "timecycle": int(timeCycle),
                        "temp": float(temp),
                        "hum": float(hum),
                        "Baterry": float(battery),

                    }
                    dt_string = "idMachine: " + idMachine + "\nBattery: " + str(battery) + "\ntemp: " + str(temp) + "\nhum: " + str(hum)
                    dlg.label_2.setText(str(dt_string))

                    try:
                        db.reference("/SensorHistory").push().set(data)
                    except Exception as er:
                        e = er
                        print("Internet Problem")

            elif type == "TempHum":
                battery = int(data[16:20], 16) / 1000
                print("Baterry: ", battery, " V")
                temp = int(data[30:34], 16) /10
                hum = int(data[34:38], 16) / 10
                print("Temperture: ", temp, " C", " Humdity: ", hum, " %")
                timeCycle = time.time()
                data = {
                    "idMachine": idMachine,
                    "type": "TempHum",
                    "timecycle": int(timeCycle),
                    "temp": float(temp),
                    "hum": float(hum),
                    "Baterry": float(battery),

                }

                try:
                    db.reference("/SensorHistory").push().set(data)
                except Exception as er:
                    e = er
                    print("Internet Problem")


def getList():
    global listS
    listS = []
    y = db.reference("/sensorList").get()
    # print(y)
    for key, value in enumerate(y):
        # print(y[value])
        listS.append(y[value])
    print(listS)

def is_port_in_use(port: int) -> bool:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def connect():
    try:
        getList()
    except KeyboardInterrupt:
        print('Interrupted')


    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(is_port_in_use(PORT))
            # if is_port_in_use(PORT):
            if s.connect_ex((HOST, PORT)) == 0:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                print("fkml")
                with conn:
                    print(f"Connected by {addr}")
                    while True:

                        data = conn.recv(10000)
                        if data:
                            # print(f"Received {data!r}")
                            getData(data)
                        if not data:
                            break
                        conn.sendall(data)
            else:
                dlg.label_2.setText("There are problem")

    except KeyboardInterrupt:
        print('Interrupted')

def main():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dlg.label.setText("Date and Time: " + str(dt_string))
    connect()





app = QtWidgets.QApplication([])
dlg = uic.loadUi("test.ui")
dlg.show()

cred = credentials.Certificate("file komate.json")
firebase_admin.initialize_app(cred,
                              {"databaseURL": "https://testqc-40e83-default-rtdb.firebaseio.com/",
                               'storageBucket': 'testqc-40e83.appspot.com'})
bucket = storage.bucket()

HOST = "10.130.1.231"  # Standard loopback interface address (localhost)
PORT = 6000  # Port to listen on (non-privileged ports are > 1023)

listS = []

battery = 0
temp = 0
hum = 0
timer = QTimer()
timer.timeout.connect(main)
timer.start(1)


app.exec()
