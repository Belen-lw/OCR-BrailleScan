import cv2
import PySimpleGUI as sg

def get_available_cameras():
    # La función cv2.videoCapture(index) intenta abrir la cámara con el índice dado.
    # Si se abre correctamente, significa que la cámara está disponible.
    available_cameras = [index for index in range(10) if cv2.VideoCapture(index).read()[0]]
    return available_cameras

def select_camera():
    available_cameras = get_available_cameras()

    layout = [
        [sg.Text('Selecciona la cámara:')],
        [sg.Listbox(values=available_cameras, size=(20, len(available_cameras)), key='-CAMERAS-')],
        [sg.Button('Aceptar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Seleccionar Cámara', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancelar'):
            window.close()
            return None
        elif event == 'Aceptar' and values['-CAMERAS-']:
            selected_camera = int(values['-CAMERAS-'][0])
            window.close()
            return selected_camera

if __name__ == '__main__':
    selected_camera = select_camera()

    if selected_camera is not None:
        sg.popup(f'Cámara seleccionada: {selected_camera}')

