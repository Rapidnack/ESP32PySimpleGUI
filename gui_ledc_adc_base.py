from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import PySimpleGUI as sg


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


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
window = sg.Window('GUI LEDC ADC BASE', layout, finalize=True,
                   auto_size_buttons=False, default_button_element_size=(12, 1))

canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas
# draw the initial plot in the window
fig_agg = draw_figure(canvas, fig)

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()
