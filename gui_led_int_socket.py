import socket
import threading
import time

import PySimpleGUI as sg


def readmessage():
    while runningflag:
        s = stream2.readline().strip()
        print(s)


def blink():
    while stopflag == False and runningflag:
        stream.write('d2 1\n')
        stream.flush()
        time.sleep(1)
        stream.write('d2 0\n')
        stream.flush()
        time.sleep(1)


layout = [[sg.Output(size=(40,10))],
          [sg.Text('IPアドレス'), sg.InputText(size=(15,1), key='-IPADDRESS-')],
          [sg.Button('OPEN'), sg.Text('未接続', size=(10,1), key='-STATUS-')],
          [sg.Button('LED ON'), sg.Button('LED OFF')],
          [sg.Button('点滅開始'), sg.Button('点滅終了')],
          [sg.Exit()]]

window = sg.Window('GUI LED INT SOCKET', layout,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

runningflag = True
stopflag = True
client = None
stream = None
client2 = None
stream2 = None

while True:
    event, values = window.read()
    #print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    elif event == 'OPEN':
        if client != None:
            client.close()
            client = None
        if client2 != None:
            client2.close()
            client2 = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((values['-IPADDRESS-'], 54001))
            stream = client.makefile(mode='rw')

            client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client2.connect((values['-IPADDRESS-'], 54002))
            stream2 = client2.makefile(mode='rw')
            threading.Thread(target=readmessage, daemon=True).start()

            window['-STATUS-'].update('接続済')
        except OSError:
            window['-STATUS-'].update('接続エラー')
            if client != None:
                client.close()
                client = None
            if client2 != None:
                client2.close()
                client2 = None

    elif event == 'LED ON':
        if client != None:
            stream.write('d2 1\n')
            stream.flush()

    elif event == 'LED OFF':
        if client != None:
            stream.write('d2 0\n')
            stream.flush()

    elif event == '点滅開始':
        if client != None and stopflag:
            stopflag = False
            threading.Thread(target=blink, daemon=True).start()

    elif event == '点滅終了':
        stopflag = True

runningflag = False
if client != None:
    client.close()
if client2 != None:
    client2.close()

window.close()
