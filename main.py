import base64
import random
import PySimpleGUI as sg
from PIL import Image, ImageTk
import os
from io import BytesIO, StringIO
import numpy
import pyperclip


def msg_window(string):
    boom = sg.Window("Output", layout=[[sg.Multiline(default_text="", size=(120, 50), k='-ml-')],
                                       [sg.Text("", expand_x=True), sg.Button("Copy"), sg.Button("Close"),
                                        sg.Text("", expand_x=True)]], relative_location=(150, -100), finalize=True)
    for each in string:
        boom['-ml-'].update(each, append=True)
        
    while True:
        event, values = boom.read()  # Noqa
        if event == sg.WINDOW_CLOSED or event == 'Close':
            break
        elif event == 'Copy':
            pyperclip.copy(boom['-ml-'].get())
    boom.close()
    boom = None


def run_image(directory):
    i = Image.open(directory)
    return ImageTk.PhotoImage(i)


def get_files(directory):
    return next(os.walk(directory), (None, None, []))[2]


def lop_extensions(directory):
    return os.path.splitext(directory)[0]


def open_file(pic_file):
    with open(f'./images/{pic_file}', 'rb') as fin:
        return fin.read()


def convert(pic_file):
    return base64.b64encode(pic_file)


def save_py(opened_file, name):  # Noqa
    with open(f'{name}.txt', 'w') as fout:
        fout.write(opened_file.decode('utf-8'))


def byte_me(pic_file):
    buffered = BytesIO()
    pic_file.save(buffered, format='PNG')
    return base64.b64encode(buffered.getvalue())


def fun_generate():
    for act in range(num_columns):
        offset_0 = act * ROWS
        col = []
        for every in range(ROWS):
            position = offset_0 + every
            if position < count:
                col.append([sg.Checkbox(text="", k=f'-toggle_{names[position]}-'),
                            sg.Button("", k=f'-b_{names[position]}-', use_ttk_buttons=True)])
        e_columns.append(sg.Column(col, expand_y=True, k=f'-column_{act}-'))
    splitz = []
    for page in range(num_pages):
        offset = page * COL_SIZE
        splitz.append(
            sg.Frame("", size=(800, 430), k=f'-page_{page}-', layout=[e_columns[offset:offset + COL_SIZE]],
                     visible=False))
    return splitz


def pic_grid():
    a_pages = [sg.Text("", expand_x=True, pad=(5, 20)), sg.Button('<< Prev')]
    for nomb in range(num_pages):
        a_pages.append(sg.Button(str(nomb + 1), k=f'-jump_{nomb + 1}-'))
    a_pages.append(sg.Button('Next >>'))
    a_pages.append(sg.Text("", expand_x=True, pad=(5, 20)))
    return [fun_generate(), a_pages,
            [sg.Text("", expand_x=True), sg.Button('Make base64', k='-make_64-'), sg.Text("", expand_x=True)],
            [sg.Text("", expand_x=True), sg.Button('Make bytes', k='-make_bytes-'), sg.Text("", expand_x=True)],
            [sg.Text("", expand_x=True), sg.Button('Quit'), sg.Text("", expand_x=True)]]


bin_folder = get_files('./images/')
count = len(bin_folder)

ROWS = 6
COL_SIZE = 6
images = {}
thumbnails = {}
names = []
pages = []
num_columns = int(numpy.floor(count / ROWS) + 1)
num_pages = int(numpy.floor(num_columns / 5)) + 1
e_columns = []
visible_frame = 0

for each in bin_folder:
    name = lop_extensions(each)
    file = f'./images/{each}'
    piled = Image.open(file)
    thumb = piled.copy()
    thumb.thumbnail((50, 50))
    thumbnails[name] = byte_me(thumb)
    
    images[name] = piled
    names.append(name)

main = sg.Window("Convert pics", layout=pic_grid(), finalize=True, size=(800, 600))

for each in names:
    strung = f'-b_{each}-'
    main[strung].update(image_data=thumbnails[each])

print(main.key_dict)
main['-page_0-'].update(visible=True)
while True:
    event, values = main.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    elif '-b_' in event:
        grab_name = event[3:-1]
        box = main[f'-toggle_{grab_name}-']
        if box.get():
            box.update(False)
        else:
            box.update(True)
    elif '-jump' in event:
        name = event[6:-1]
        main[f'-page_{visible_frame}-'].update(visible=False)
        visible_frame = int(name) - 1
        main[f'-page_{visible_frame}-'].update(visible=True)
    elif event == 'Next >>':
        main[f'-page_{visible_frame}-'].update(visible=False)
        if visible_frame < num_pages - 1:
            visible_frame += 1
        main[f'-page_{visible_frame}-'].update(visible=True)
    elif event == '<< Prev':
        main[f'-page_{visible_frame}-'].update(visible=False)
        if visible_frame > 0:
            visible_frame -= 1
        main[f'-page_{visible_frame}-'].update(visible=True)
    elif event == '-make_64-':
        checked = []
        for each in values:
            if values[each]:
                name = each[8:-1]
                s64 = str(byte_me(images[name]), 'utf-8')
                checked.append(f'{name} = "{s64}"')
        main['Quit'].update(disabled=True)
        msg_window(checked)
        main['Quit'].update(disabled=False)

main.close()
