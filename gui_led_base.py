import PySimpleGUI as sg


layout = [[sg.Text('IPアドレス'), sg.InputText(size=(15,1), key='-IPADDRESS-')],
          [sg.Button('OPEN'), sg.Text('未接続', size=(10,1), key='-STATUS-')],
          [sg.Button('LED ON'), sg.Button('LED OFF')],
          [sg.Button('点滅開始'), sg.Button('点滅終了')],
          [sg.Exit()]]

window = sg.Window('GUI LED BASE', layout,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()
