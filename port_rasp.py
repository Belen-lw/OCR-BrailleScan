import serial.tools.list_ports
import PySimpleGUI as sg

def get_usb_ports():
    # Obtener una lista de todos los puertos COM
    ports = [port.device for port in serial.tools.list_ports.comports()]

    # Filtrar los puertos que contienen "usb"
    usb_ports = [port for port in ports if "usb" in port.lower()]

    return usb_ports

def select_usb_port():
    usb_ports = get_usb_ports()

    layout = [
        [sg.Text('Selecciona el puerto USB:')],
        [sg.Listbox(values=usb_ports, size=(20, len(usb_ports)), key='-USB_PORTS-')],
        [sg.Button('Aceptar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Seleccionar Puerto USB', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancelar'):
            window.close()
            return None
        elif event == 'Aceptar' and values['-USB_PORTS-']:
            selected_usb_port = values['-USB_PORTS-'][0]
            window.close()
            return selected_usb_port

if __name__ == '__main__':
    selected_usb_port = select_usb_port()

    if selected_usb_port:
        sg.popup(f'Puerto USB seleccionado: {selected_usb_port}')
