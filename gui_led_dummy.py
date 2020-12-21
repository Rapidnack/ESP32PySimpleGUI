import threading
import time

import PySimpleGUI as sg


def blink():
    while stopflag == False and runningflag:
        print('コマンド送信: d2 1')
        time.sleep(1)
        print('コマンド送信: d2 0')
        time.sleep(1)


layout = [[sg.Text('IPアドレス'), sg.InputText(size=(15,1), key='-IPADDRESS-')],
          [sg.Button('OPEN'), sg.Text('未接続', size=(10,1), key='-STATUS-')],
          [sg.Button('LED ON'), sg.Button('LED OFF')],
          [sg.Button('点滅開始'), sg.Button('点滅終了')],
          [sg.Exit()]]

window = sg.Window('GUI LED DUMMY', layout,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

runningflag = True
stopflag = True

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    elif event == 'OPEN':
        window['-STATUS-'].update('接続済')

    elif event == 'LED ON':
        print('コマンド送信: d2 1')

    elif event == 'LED OFF':
        print('コマンド送信: d2 0')

    elif event == '点滅開始':
        if stopflag:
            stopflag = False
            threading.Thread(target=blink, daemon=True).start()

    elif event == '点滅終了':
        stopflag = True

runningflag = False

window.close()
