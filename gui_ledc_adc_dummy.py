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
        high = 5 + int(dummyangle / 180.0 * 20)
        low = 27 - high
        i = 0
        v = '60'
        for x in range(3):
            v += f' 0 {i * 100}'
            i += 1
        for x in range(high):
            v += f' 4095 {i * 100}'
            i += 1
        for x in range(low):
            v += f' 0 {i * 100}'
            i += 1
        #print(v)
        try:
            window.write_event_value('-THREAD-', v)
        except:
            pass
        time.sleep(1)


fig = plt.figure(figsize=(6, 4))
figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
ax = fig.add_subplot(111)

layout = [[sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-')],
          [sg.Text('IPアドレス'), sg.InputText(size=(15,1), key='-IPADDRESS-')],
          [sg.Button('OPEN'), sg.Text('未接続', size=(10,1), key='-STATUS-')],
          [sg.Text('角度'),
           sg.Slider(range=(0, 180), default_value=90, orientation='h',
                     size=(34, 20), key='-ANGLE-', enable_events=True)],
          [sg.Button('取得開始'), sg.Button('取得終了')],
          [sg.Exit()]]

# create the form and show it without the plot
window = sg.Window('GUI LEDC ADC DUMMY', layout, finalize=True,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas
# draw the initial plot in the window
fig_agg = draw_figure(canvas, fig)

runningflag = True
stopflag = True
dummyangle = 90

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

    elif event == '-ANGLE-':
        dummyangle = values[event]

    elif event == '取得開始':
        if stopflag:
            ax.cla()
            ax.set_xlabel('時間[ms]', fontname='MS Gothic')
            ax.set_ylabel('電圧[V]', fontname='MS Gothic')
            ax.set_ylim(0, 3.5)
            x = []
            y = []
            lines, = ax.plot(x, y, color='purple', label='サーボパルス')
            ax.legend(prop={'family':'MS Gothic'})
            fig_agg.draw()
            stopflag = False
            threading.Thread(target=read, daemon=True).start()

    elif event == '取得終了':
        stopflag = True

    elif event == '-THREAD-':
        a = values[event].split(' ')

        # データを時刻順に並べ替える
        xy = []
        for i in range(1, len(a), 2):
            xn = (float(a[i + 1]) / 1000.0)
            yn = (float(a[i]) / 4095.0 * 3.3)
            xy.append((xn, yn))
        sortedxy = sorted(xy, key = lambda x:x[0])
        x = [p[0] for p in sortedxy]
        y = [p[1] for p in sortedxy]

        # 10%の位置の時刻を0とする
        trigpos = round((len(x) * 10) / 100)
        trigx = x[trigpos]
        x = [p - trigx for p in x]

        lines.set_data(x, y)
        if len(x) >= 2:
            ax.set_xlim(min(x), max(x))
        fig_agg.draw()

runningflag = False

window.close()
