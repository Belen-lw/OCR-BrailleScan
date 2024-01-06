import PySimpleGUI as sg
import cv2
import datetime
from ImageProcc import Bordes, ImagetoText
import numpy as np
import serial
import subprocess
import requests
import os
from time import sleep
theme_dict = {'BACKGROUND': '#2b475d',
              'TEXT': '#FFFFFF',
              'INPUT': '#F2EFE8',
              'TEXT_INPUT': '#000000',
              'SCROLL': '#F2EFE8',
              'BUTTON': ('#0B164D', '#B3D2EB'),
              'PROGRESS': ('#FFFFFF', '#C7D5E0'),
              'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#2b475d'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((20, 20), (20, 20))
BPAD_LEFT = ((20, 10), (0, 10))
BPAD_LEFT_INSIDE = (0, 7)
BPAD_RIGHT = ((10, 20), (10, 20))


#-------------------AUTHOMATIC MODE PARAMS-----------------------
heightImg = 1100
widthImg  = 790
threshold_value = 188
kernel_size = 3
brillo_factor = 1.6
threshold_type = cv2.THRESH_BINARY
a=41 #3
s=4 #5
remove_border = 1 #remove pixels from border to avoid noise
th1=50
th2=150
keybar="AIzaSyCl3izNl0zJObfDxVpf30sGMl_uzaXGZ2g"
pathT='E:\\Tesseract-OCR\\tesseract'
jsonF='ocr-braillescan.json'

#----------------------DASHBOARD PARAMS ------------------------
P2camsize=(665,460)
fondoP2=cv2.imread('logoO.png')
fondoP2=cv2.resize(fondoP2,(P2camsize))
fondoP2A=cv2.imencode('.png', fondoP2)[1].tobytes()
Pf=(500,500)
pF=cv2.imread('logoO.png')
pp=cv2.resize(cv2.imread('logoO.png'),(P2camsize))
fondo=cv2.imencode('.png', pp)[1].tobytes()
PRed=(100,100)
with open('wifi.png', 'rb') as f:
    fondoP2W = f.read()


cap = cv2.VideoCapture(0)
with open('tok1 (1).png', 'rb') as f:
    toggle_btn_on = f.read()
with open('tok2 (1).png', 'rb') as f:
    toggle_btn_off = f.read()
global se
se=True

ocrGLOB, autGLOB=True,1
#------------------------Functions-------------------------
def comprobar_conexion():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
    # For Raspberry
    # try:
    #     # Intenta realizar un ping a un servidor de Google
    #     subprocess.run(['ping', '-c', '4', '8.8.8.8'], check=True)
    #     return True
    # except subprocess.CalledProcessError:
    #     return False

def establecer_conexion_wifi(ssid, password):
    try:
        # Configura la conexión Wi-Fi
        subprocess.run(['sudo', 'raspi-config', 'nonint', 'do_wifi_ssid_passphrase', ssid, password], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al establecer la conexión Wi-Fi: {e}")
        return False
def wifiW():
    layout = [
        [sg.Text('Nombre de red (SSID):'), sg.InputText(key='-SSID-')],
        [sg.Text('Contraseña:'), sg.InputText(key='-PASSWORD-', password_char='*')],
        [sg.Button('Conectar')],
        [sg.Text('', size=(20, 1), key='-STATUS-')]
    ]
    window5 = sg.Window('Configuración Wi-Fi', layout)

    while True:
        event, values = window5.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Conectar':
            ssid = values['-SSID-']
            password = values['-PASSWORD-']

            if ssid and password:
                pass
            #     if establecer_conexion_wifi(ssid, password):
            #         window5['-STATUS-'].update('Conexión exitosa', text_color='green')
            #         window5.close()
            #         break
            #     else:
            #         window5['-STATUS-'].update('Error al establecer la conexión', text_color='red')
            # else:
            #     window5['-STATUS-'].update('Ingrese SSID y contraseña', text_color='red')

    window5.close()
def WindowPrint():

    Simg = cv2.imread('scanned.png')
    if ocrGLOB and autGLOB ==1:
        print(ocrGLOB,autGLOB)
        sg.popup("Estas con las configuraciones de Google, para cambiar ve a opciones avanzadas",title='ADVERTENCIA')  
    if ocrGLOB==True:
        #text=ImagetoText.GOO_detect_text(i,jsonF)
        print('ocr con google is uma cosa maeravilosa')
        text='ocr con google is uma cosa maeravilosa'
    else:
        text =ImagetoText.Tree_detect_text(Simg,pathT) #psm --11
        text=text.replace("\n", " ")
    if autGLOB == 1:
        CorrectText=ImagetoText.A_corrector(text,keybar)
    elif autGLOB ==2:
        CorrectText=ImagetoText.M_corrector(text)
    else:
        CorrectText=text
    layout3 = [
    [sg.Text('Texto Corregido:')],
    [sg.Multiline(default_text=CorrectText,key='-keybox-', size=(40, 40))],
    [sg.Button('Volver'),sg.Button('Imprimir')]
    ]
    window3 = sg.Window('Imprimir', layout3, margins=(0, 0), background_color=BORDER_COLOR,
                   grab_anywhere=True)
    #window3['-keybox-'].update(value=CorrectTextM)
    while True:  # <-- Mueve el while True aquí dentro
        evPrint, valPrint = window3.read()

        if evPrint == 'Imprimir':
            gcode_commands = ImagetoText.text_to__braille_gcode(CorrectText)
            port_name = "COM5"
            baud_rate = 250000
            ser = serial.Serial(port_name, baud_rate, timeout=1)
            sleep(1)
            ImagetoText.write_to_serial_port(ser, "G90")
            ImagetoText.write_to_serial_port(ser, "M84")
            ImagetoText.write_to_serial_port(ser, "G28 X")
            ImagetoText.write_to_serial_port(ser, "G28 Y")
            ImagetoText.write_to_serial_port(ser, "G92 Y-30")
            for comando in gcode_commands:
                ImagetoText.write_to_serial_port(ser, comando)
                sleep(0.2)
            ser.close()
            
            print(valPrint)
        elif evPrint == sg.WIN_CLOSED or evPrint=='Volver':
            window3.close()
            break
       

def Manualconfig():
    sg.popup("Automatico desde manual: "+str(se))
    #Aca la funcion de manual
def Opciones():
    
    global ocrGLOB, autGLOB
    ocrT='GOOGLE OCR'
    autT='AUTOCORRECTOR TESSERACT'
    layout4 = [
    [sg.Text('Opciones de Escaner:')],
    [sg.Text('Modelo OCR:  '),sg.Radio('GOOGLE CLOUD', 1, key='-OCR-')],
    [sg.Text('Modelo OCR:  '),sg.Radio('PYTESSERACT',1, key='-OCR-')],
    [sg.Text('Modelo AUTOCORRECTOR:  '),sg.Radio('GOOGLE CLOUD', 2,key='-AUTOCORRECTOR1-')],
    [sg.Text('Modelo AUTOCORRECTOR:  '),sg.Radio('PYAUTOCORRECT',2,key='-AUTOCORRECTOR2-')],
    [sg.Text('Modelo AUTOCORRECTOR:  '),sg.Radio('NO APLICAR',2,key='-AUTOCORRECTOR3-')],
    [sg.Button('Guardar Cambios'),sg.Button('Cancelar')]
    ]
    window4 = sg.Window('Opciones', layout4, margins=(0, 0), background_color='#0f092c',
                   grab_anywhere=True)
    while True:  # <-- Mueve el while True aquí dentro
            evop, valop = window4.read()
            # Imprime el texto correspondiente
            if evop == sg.WIN_CLOSED or evop == 'Cancelar':
                sg.popup(f"Esto mantendrá las configuraciones previas de:\n {ocrT} y {autT}",title='ADVERTENCIA')  
                window4.close()
                break
            elif evop =='Guardar Cambios':
                ocr_model = valop['-OCR-']
                autocorrector_model = valop['-AUTOCORRECTOR1-']
                print(f"Modelo OCR escogido: {ocr_model}")
                print(f"Modelo AUTOCORRECTOR escogido: {autocorrector_model,valop['-AUTOCORRECTOR2-'],valop['-AUTOCORRECTOR3-']}")
                if ocr_model:
                    ocrGLOB=True
                    ocrT='GOOGLE OCR'
                elif ocr_model == False:
                    ocrGLOB=False
                    ocrT='PYTESSERACT'
                if valop['-AUTOCORRECTOR1-']:
                    autGLOB = 1
                    autT='AUTOCORRECTOR GOOGLE'
                if valop['-AUTOCORRECTOR2-']:
                    autGLOB = 2
                    autT='AUTOCORRECTOR TESSERACT'
                if valop['-AUTOCORRECTOR3-']:
                    autGLOB = 3
                    autT=' SIN AUTOCORRECTOR'
                break
    window4.close()            
def capturar_video(cap,window2):
    
    while True:
        ret, frame = cap.read()

        if not ret:
            sg.popup_error("Error al capturar video desde la cámara.")
            break

        # Convertir el fotograma de OpenCV a formato que PySimpleGUI pueda mostrar
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()

        window2['-CAMARA-'].update(data=imgbytes)

        evento, _ = window2.read(timeout=20)
        if evento == 'salir de cámara':
            frame=fondoP2.copy()
            frame=cv2.resize(fondoP2.copy(), P2camsize)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window2['-CAMARA-'].update(data=imgbytes)
            break

    cap.release()
    
def mainBsc():
    global se
    cap=cv2.VideoCapture(1)   
    top_banner = [
        [sg.Text('BrailleScan', font='Any 25', background_color=DARK_HEADER_COLOR),
        sg.Text(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), font='Any 20', background_color=DARK_HEADER_COLOR)]]
    block_2 = [
        #[sg.Text('Block 2', font='Any 10')],
        [sg.Button('Mostrar cámara I',size=(9,3), font='Any 12'), sg.Button('Mostrar cámara D',size=(9,3), font='Any 12')],
        [sg.Button('Escanear I',size=(9,3), font='Any 12'), sg.Button('Escanear D',size=(9,3), font='Any 12')],    
        ]

    block_3 = [
        #[sg.Text('Block 3', font='Any 10')],
        [sg.Button('Imprimir',size=(9,3), font='Any 12'),sg.Button('Opciones Avanzadas',size=(9,3), font='Any 12') ],
        [sg.Button('Exit',size=(20,2), font='Any 12')]]

    block_4 = [
        [sg.Column([[sg.Button('salir de cámara'), 
                    sg.Text('Manual'),
                    sg.Button(image_data=toggle_btn_off, key='-TOGGLE-GRAPHIC-', button_color=( sg.theme_background_color(), sg.theme_background_color()), border_width=0, metadata=False)]],
                    justification='right'),
                    sg.Text('Automático')],
        [sg.Image(data=fondoP2A, key='-CAMARA-', size=P2camsize)], 
        ]
    layout2 = [
        [sg.Column(top_banner, size=(960, 60), pad=(0, 0), background_color=DARK_HEADER_COLOR)],
        [sg.Column([[sg.Column(block_2, size=(220, 150), pad=BPAD_LEFT_INSIDE)],
                    [sg.Column(block_3, size=(220, 150), pad=BPAD_LEFT_INSIDE)]], pad=BPAD_LEFT, background_color=BORDER_COLOR),
        sg.Column(block_4, size=(680, 540), pad=BPAD_RIGHT)]]

    window2 = sg.Window('Dashboard PySimpleGUI-Style', layout2, margins=(0, 0), background_color=BORDER_COLOR, no_titlebar=True,
                    grab_anywhere=True)

    while True:  # Event Loop
        event, values = window2.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            
            break
        
        elif event == 'Mostrar cámara D':
            #sg.popup('Button a pressed!')
            cap = cv2.VideoCapture(0)
            capturar_video(cap,window2)
            frame==cv2.resize(fondoP2.copy(), P2camsize)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window2['-CAMARA-'].update(data=imgbytes)
        elif event == 'Mostrar cámara I':
            #sg.popup('Button B pressed!')
            cap = cv2.VideoCapture(1)
            capturar_video(cap,window2)
            frame=cv2.resize(fondoP2.copy(), P2camsize)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window2['-CAMARA-'].update(data=imgbytes)
            
        elif event == 'Escanear I':
            cap = cv2.VideoCapture(1)
            ret,img =cap.read()
            height, width = img.shape[:2]
            imgCol = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
            if width > height:
                #print(height,width)
                uimage =cv2.rotate(imgCol, cv2.ROTATE_90_CLOCKWISE)
            else:
                pass
            if se:
                imgWarpGray,imgContours,imgBigContour = Bordes.Contorns(uimage,widthImg, heightImg,brillo_factor,threshold_value)
                #process to get text from image
                #cv2.imshow('taken',imgContours)
                #--------------------------------------------------------------------------------------------------------------------------------------
                if imgWarpGray is not None or imgBigContour is not None:
                    imageB = cv2.multiply(imgWarpGray, np.array([0.3]))
                    i=cv2.adaptiveThreshold(imageB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, a, s)
                    #cv2.imshow("Result2",i)
                    cv2.imwrite('scanned.png',i)
                    frame=cv2.resize(cv2.cvtColor(i, cv2.COLOR_GRAY2RGB), P2camsize)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
                else:
                    sg.popup_error('Hoja no detectada, intente nuevamente',title='ERROR')
                    frame=cv2.rotate(imgContours.copy(), cv2.ROTATE_90_COUNTERCLOCKWISE)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
            else:
                Manualconfig()
        elif event == 'Escanear D':
            cap = cv2.VideoCapture(0)
            ret,img =cap.read()
            height, width = img.shape[:2]
            imgCol = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
            if width > height:
                #print(height,width)
                uimage =cv2.rotate(imgCol, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                pass
            if se:
                imgWarpGray,imgContours,imgBigContour = Bordes.Contorns(uimage,widthImg, heightImg,brillo_factor,threshold_value)
                #process to get text from image
                #--------------------------------------------------------------------------------------------------------------------------------------
                if imgWarpGray is not None or imgBigContour is not None:
                    imageB = cv2.multiply(imgWarpGray, np.array([0.3]))
                    i=cv2.adaptiveThreshold(imageB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, a, s)
                    #cv2.imshow("Result2",i)
                    cv2.imwrite('scanned.png',i)
                    
                    frame=cv2.resize(cv2.cvtColor(i, cv2.COLOR_GRAY2RGB), P2camsize)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
                else:
                    sg.popup_error('Hoja no detectada, intente nuevamente',title='ERROR')
                    frame=cv2.rotate(imgContours.copy(), cv2.ROTATE_90_CLOCKWISE)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
            else:
                Manualconfig()
        elif event == 'salir de cámara':
            frame=fondoP2.copy()
            frame=cv2.resize(fondoP2.copy(), P2camsize)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window2['-CAMARA-'].update(data=imgbytes)
            
        elif event == '-TOGGLE-GRAPHIC-':  # if the graphical button that changes images
            window2['-TOGGLE-GRAPHIC-'].metadata = not window2['-TOGGLE-GRAPHIC-'].metadata
            window2['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_on if window2['-TOGGLE-GRAPHIC-'].metadata else toggle_btn_off)

            
            
        elif event == 'Imprimir':
            WindowPrint()
        elif event == 'Opciones Avanzadas':
            Opciones()    
        if window2['-TOGGLE-GRAPHIC-'].metadata:
            #This is manual config:
            se=False
            #sg.popup("Automatico: "+str(se))
        else:
            #This is Automatic config:
            se=True
            #sg.popup("Automatico"+str(se))    
    window2.close()
    
    cap.release()


#--------------------LOGIN-----------------------------------------


top  = [[sg.Text('BRAILLESCAN', size=(50,1), justification='c', pad=BPAD_TOP, font='Any 20')]]

block_3 = [[sg.Button('Empezar',size=(20,3), font='Any 16')],
    [sg.Button('Apagar',size=(20,3), font='Any 16')] ]


block_2 = [[sg.Column([[sg.Button(image_data=fondoP2W, size=(30, 2), font='Any 1',key='-wifi-')],
                       [sg.Text('Conecta el internet', font='Any 13')]],
                      element_justification='center')]]


block_4 = [[sg.Image(data=fondo, size=Pf)]]


layout = [[sg.Column(top, size=(610, 100), pad=BPAD_TOP)],
          [sg.Column([[sg.Column(block_3, size=(260, 190),  pad=BPAD_LEFT_INSIDE)],
              [sg.Column(block_2, size=(270,150), pad=(10,1))]
                      ], pad=BPAD_LEFT, background_color='#2b475d'),
           sg.Column(block_4, size=(500, 500), pad=BPAD_RIGHT)]]

window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color='#2b475d', no_titlebar=True, grab_anywhere=True)
b=False
while True:
    event1,value1=window.read()
    if event1 == 'Empezar'and b:
        window.hide()
        mainBsc()
        window.un_hide()
        b=False
    elif event1 == 'Empezar'and not b:
        sg.popup("Primero debes comprobar la conexión a internet",title='ADVERTENCIA')     
    elif event1 == '-wifi-':
        b=True
        if comprobar_conexion():
            sg.popup_ok("¡Estás conectado a Internet!",title='CONFIRMACIÓN')
        else:
            # No hay conexión
            sg.popup_error("No estás conectado a Internet",title='CONFIRMACIÓN')
        #window.hide()
            wifiW()
        #window.un_hide()
    elif event1 == 'Apagar' or event1 == sg.WIN_CLOSED:
        rsp=sg.popup_ok_cancel("El sistema se apagará de inmediato",title='ADVERTENCIA')
        if rsp == 'OK':
            print('apagar')
            #os.system("sudo shutdown -h now")
            break
window.close()
    