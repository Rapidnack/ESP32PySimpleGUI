import socket
import threading
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import PySimpleGUI as sg


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def read():
    while stopflag == False and runningflag:
        stream.write('leddata\n')
        stream.flush()
        v = stream.readline().strip()
        #print(v)
        try:
            window.write_event_value('-THREAD-', v)
        except:
            pass
        time.sleep(0.1)


fig = plt.figure(figsize=(6, 4))
figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
ax = fig.add_subplot(111)

layout = [[sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-')],
          [sg.Text('IPアドレス'), sg.InputText(size=(15,1), key='-IPADDRESS-')],
          [sg.Button('OPEN'), sg.Text('未接続', size=(10,1), key='-STATUS-')],
          [sg.Button('LED ON'), sg.Button('LED OFF')],
          [sg.Button('取得開始'), sg.Button('取得終了')],
          [sg.Exit()]]

# create the form and show it without the plot
window = sg.Window('GUI LED ADC SOCKET', layout, finalize=True,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas
# draw the initial plot in the window
fig_agg = draw_figure(canvas, fig)

runningflag = True
stopflag = True
client = None
stream = None

while True:
    event, values = window.read()
    #print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    elif event == 'OPEN':
        if client != None:
            client.close()
            client = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((values['-IPADDRESS-'], 54001))
            stream = client.makefile(mode='rw')
            window['-STATUS-'].update('接続中')
        except OSError:
            window['-STATUS-'].update('接続エラー')
            client = None

    elif event == 'LED ON':
        if client != None:
            stream.write('d2 1\n')
            stream.flush()

    elif event == 'LED OFF':
        if client != None:
            stream.write('d2 0\n')
            stream.flush()

    elif event == '取得開始':
        if client != None and stopflag:
            ax.cla()
            ax.set_xlabel('時間[s]', fontname='MS Gothic')
            ax.set_ylabel('電圧[V]', fontname='MS Gothic')
            ax.set_ylim(0, 3.5)
            x = []
            y = []
            lines, = ax.plot(x, y, color='purple', label='LED')
            ax.legend()
            fig_agg.draw()
            stopflag = False
            threading.Thread(target=read, daemon=True).start()

    elif event == '取得終了':
        stopflag = True

    elif event == '-THREAD-':
        a = values[event].split(' ')
        if len(x) == 100:
            x.pop(0)
            y.pop(0)
        x.append(float(a[2]) / 1000.0)
        y.append(float(a[1]) / 4095.0 * 3.3)
        lines.set_data(x, y)
        if len(x) >= 2:
            ax.set_xlim(min(x), max(x))
        fig_agg.draw()

runningflag = False
if client != None:
    client.close()

window.close()
