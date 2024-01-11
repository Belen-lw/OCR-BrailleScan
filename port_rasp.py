import serial.tools.list_ports
import PySimpleGUI as sg

def encontrar_puerto_usb_raspberry():
    # Obtener la lista de puertos disponibles
    puertos_disponibles = [port.device for port in serial.tools.list_ports.comports()]

    # Filtrar los puertos que siguen la convención "/dev/ttyUSB"
    puertos_usb_raspberry = [puerto for puerto in puertos_disponibles if '/dev/ttyUSB' in puerto]

    if not puertos_usb_raspberry:
        sg.popup_error('No se encontraron puertos USB en la convención /dev/ttyUSB.')
        return None

    # Devolver el primer puerto USB detectado
    return puertos_usb_raspberry[0]

# Ejemplo de uso:
puerto_usb_raspberry = encontrar_puerto_usb_raspberry()
if puerto_usb_raspberry:
    sg.popup(f'Puerto USB detectado en Raspberry: {puerto_usb_raspberry}')
    print(f'Puerto USB seleccionado: {puerto_usb_raspberry}')
    # Ahora puedes usar el puerto_usb_raspberry para la comunicación serial en tu Raspberry Pi
