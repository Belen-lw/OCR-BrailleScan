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
              'BORDER': 0.2, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#2b475d'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((15, 15), (15,15))
BPAD_LEFT = ((20, 10), (0, 10))
BPAD_LEFT_INSIDE = (0, 2)
BPAD_RIGHT = ((8, 8), (8, 8))


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
#----------------MANUAL PARAMS--------------------------
lim1=3
lim2=3

#--------------OCR PARAMS---------------------------------
keybar="AIzaSyCl3izNl0zJObfDxVpf30sGMl_uzaXGZ2g"
pathT='E:\\Tesseract-OCR\\tesseract'
jsonF='ocr-braillescan.json'

#----------------------DASHBOARD PARAMS ------------------------
P2camsize=(480,350)
fondoP2=cv2.imread('logoO.png')
fondoP2=cv2.resize(fondoP2,(P2camsize))
fondoP2A=cv2.imencode('.png', fondoP2)[1].tobytes()
Pf=(480,350)
pF=cv2.imread('logoO.png')
pp=cv2.resize(cv2.imread('logoO.png'),(Pf))
fondo=cv2.imencode('.png', pp)[1].tobytes()
PRed=(40,50)
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
    if ocrGLOB==True:
        text=ImagetoText.GOO_detect_text(Simg,jsonF)
        #print('ocr con google is uma cosa maeravilosa')
        #text='ocr con google is uma cosa maeravilosa'
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
    [sg.Multiline(default_text=CorrectText,key='-keybox-', size=(50, 30),font="Any 10")],
    [sg.Button('Volver'),sg.Button('Imprimir')]
    ]
    window3 = sg.Window('Imprimir', layout3, margins=(0, 0), background_color=BORDER_COLOR,
                   grab_anywhere=True)
    #window3['-keybox-'].update(value=CorrectTextM)
    while True:  # <-- Mueve el while True aquí dentro
        evPrint, valPrint = window3.read()

        if evPrint == 'Imprimir':
            gcode_commands = ImagetoText.text_to__braille_gcode(CorrectText)
            #port_name = 'COM11'
            port_name = "/dev/ttyUSB0"
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
       

def Manualconfig(imageCol):
    #imageCol = cv2.cvtColor(cv2.imread('img\FotoA_1.png'), cv2.COLOR_BGR2RGB)
    original_image = imageCol.copy()
    uimage = cv2.cvtColor(imageCol, cv2.COLOR_RGB2GRAY)

    height, width = uimage.shape[:2]
    heightImg = 1100
    widthImg  = 790
    # Parámetros iniciales
    threshold_value = 198
    kernel_size = 3
    brillo_factor = 1.6
    threshold_type = cv2.THRESH_BINARY
    a = 11
    s = 2
    th1 = 50
    th2 = 150
    lim1=3
    lim2=3
    # Crear una ventana de diseño
    layout = [
        [sg.Image(data=cv2.imencode('.png', imageCol)[1].tobytes(), key='image')],
        [sg.Text('Threshold Type:'),
        sg.Combo(['Binary', 'Otsu', 'Adaptive Mean', 'Adaptive Gaussian'], default_value='Binary', key='threshold_type', enable_events=True),
        sg.Text('límite 1:'), sg.Slider(range=(3,99,2), default_value=threshold_value, orientation='h', key='-L1-',font='Any 7')],
        [sg.Text('Threshold Value:'), sg.Slider(range=(0, 255), default_value=threshold_value, orientation='h', key='-threshold_value-',font='Any 7'),
        sg.Text('   límite 2:'), sg.Slider(range=(3,99,2), default_value=threshold_value, orientation='h', key='-L2-',font='Any 7')],
        [sg.Text('Kernel Size:'), sg.Slider(range=(3, 25), default_value=kernel_size, orientation='h', key='-kernel_size-',font='Any 7')],
        [sg.Text('Brightness Factor:'), sg.Slider(range=(0.0, 2.0), resolution=0.1, default_value=brillo_factor, orientation='h', key='-brillo_factor-',font='Any 7')],
        [sg.Button('Cortar'),sg.Button('Guardar')]
    ]

    window6 = sg.Window('Image Processing GUI', layout, finalize=True)
    a=False
    b=False
    c=False
    #print(lim1,lim2)
    while True:
        event, values = window6.read(timeout=0)  # Usar timeout=0 para que no bloquee el programa

        if event == sg.WIN_CLOSED:
            break
        elif event == sg.TIMEOUT_EVENT:
            # Aplicar cambios según los valores de los sliders y el combo
            threshold_type = values['threshold_type']
            threshold_value = int(values['-threshold_value-'])
            #print(threshold_type)
            kernel_size = int(values['-kernel_size-'])
            brillo_factor = float(values['-brillo_factor-'])
            lim1=int(values['-L1-'])
            lim2=int(values['-L2-'])
            lim1 = lim1 if lim1 % 2 != 0 else lim1 + 1
            lim2 = lim2 if lim2 % 2 != 0 else lim2 + 1
            
            # Operaciones en la imagen
            imagen_brillante = cv2.multiply(uimage, np.array([brillo_factor]))
            if threshold_type == 'Binary':
                _, thresholded_image = cv2.threshold(imagen_brillante, threshold_value, 255, cv2.THRESH_BINARY)
            elif threshold_type == 'Otsu':
                _, thresholded_image = cv2.threshold(imagen_brillante, threshold_value, 255, cv2.THRESH_TOZERO)
            elif threshold_type == 'Adaptive Mean':
                thresholded_image = cv2.adaptiveThreshold(imagen_brillante, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, lim1, lim2)
            elif threshold_type == 'Adaptive Gaussian':
                thresholded_image = cv2.adaptiveThreshold(imagen_brillante, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, lim1,lim2)
            
            #_, thresholded_image = cv2.threshold(imagen_brillante, threshold_value, 255, cv2.THRESH_BINARY)
            if b:
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                uimage=original_image.copy()
                iC2=cv2.resize(thresholded_image,(480,350))
            else:
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                dila = cv2.morphologyEx(thresholded_image, cv2.MORPH_CLOSE, kernel)
                #cv2.imshow('tit',dila)
                # Mostrar la imagen resultante en la GUI
                iC = original_image.copy()
                contornos, jerarquia = cv2.findContours(dila, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for idx, contorno in enumerate(contornos):
                    epsilon = 0.03 * cv2.arcLength(contorno, True)
                    approx = cv2.approxPolyDP(contorno, epsilon, True)
                    
                    if len(approx) == 4:
                        cv2.drawContours(iC, [contorno], 0, (0, 255, 0), 2)
                        iC2 = cv2.resize(iC.copy(),(480,350))
                        a=True
                    else:
                        a=False
        
            window6['image'].update(data=cv2.imencode('.png', iC2)[1].tobytes())
        elif event == 'Cortar' and a:
            b=True
            sg.popup('cortar?')
            imgWarpGray,_,imgBigContour = Bordes.Contorns(imageCol,widthImg, heightImg,brillo_factor,threshold_value)
            original_image=imgWarpGray.copy()
            uimage=cv2.resize(original_image,(width,height))
            window6['image'].update(data=cv2.imencode('.png', uimage)[1].tobytes())
            #cv2.imshow('hool',imgWarpGray)
        elif event == 'Guardar' and b:
            #saveI=cv2.rotate(thresholded_image.copy(), cv2.ROTATE_90_CLOCKWISE)
            c=True
            saveI=thresholded_image.copy()
            saveI2=cv2.resize(saveI.copy(),(480,250))
            cv2.imwrite('scanned.png',saveI)
            break
    
    window6.close()
    if c:
        return saveI2
    else:
        return None
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
                window4.hide()
                sg.popup(f"Esto mantendrá las configuraciones previas de:\n {ocrT} y {autT}",title='ADVERTENCIA')  
                window4.un_hide()
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
            window2.hide()
            sg.popup_error("Error al capturar video desde la cámara.")
            
            window2.un_hide()
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
    cap=cv2.VideoCapture(0)   
    top_banner = [
        [sg.Text('BrailleScan                ', font='Any 20', background_color=DARK_HEADER_COLOR,pad=(BPAD_TOP)),
        sg.Text(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), font='Any 14', background_color=DARK_HEADER_COLOR)]]
    block_2 = [
        #[sg.Text('Block 2', font='Any 8')],
        [sg.Button('Mostrar cámara I', size=(9, 2), font='Any 8'), sg.Button('Mostrar cámara D', size=(9, 2), font='Any 8')],
        [sg.Button('Escanear I', size=(9, 2), font='Any 8'), sg.Button('Escanear D', size=(9, 2), font='Any 8')],
    ]

    block_3 = [
        #[sg.Text('Block 3', font='Any 8')],
        [sg.Button('Imprimir', size=(9, 2), font='Any 8'), sg.Button('Opciones Avanzadas', size=(9, 2), font='Any 8')],
        [sg.Button('Exit', size=(22, 1), font='Any 8')],
    ]

    block_4 = [
        [sg.Column([[sg.Button('salir de cámara'),
                    sg.Text('Manual', font='Any 8'),
                    sg.Button(image_data=toggle_btn_off, key='-TOGGLE-GRAPHIC-', button_color=( sg.theme_background_color(), sg.theme_background_color()), border_width=0, metadata=False)]],
                    justification='left'),
                    sg.Text('Automático', font='Any 8')],
        [sg.Image(data=fondoP2A, key='-CAMARA-', size=(480, 380))], 
    ]
    layout2 = [
        [sg.Column(top_banner, size=(630, 50), pad=(0, 0), background_color=DARK_HEADER_COLOR)],
        [sg.Column([[sg.Column(block_2, size=(190, 100))],
                    [sg.Column(block_3, size=(190, 100))]], background_color=BORDER_COLOR),
        sg.Column(block_4, size=(410, 390))]]
    window2 = sg.Window('Dashboard PySimpleGUI-Style', layout2, margins=(0, 0), background_color=BORDER_COLOR, no_titlebar=True,
                    grab_anywhere=True)

    while True:  # Event Loop
        event, values = window2.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            
            break
        
        elif event == 'Mostrar cámara D':
            #sg.popup('Button a pressed!')
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if not ret:
                window2.hide()
                sg.popup_error("camara Derecha no conectada")
                window2.un_hide()
            else:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        window2.hide()
                        sg.popup_error("Error al capturar video desde la cámara.")                 
                        window2.un_hide()
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
                
                frame==cv2.resize(fondoP2.copy(), P2camsize)
                imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                window2['-CAMARA-'].update(data=imgbytes)
        elif event == 'Mostrar cámara I':
            cap1 = cv2.VideoCapture(1)
            ret, frame = cap1.read()
            if not ret:
                window2.hide()
                sg.popup_error("camara Izquierda no conectada")
                window2.un_hide()
            else:
                while True:
                    ret, frame = cap1.read()
                    if not ret:
                        window2.hide()
                        sg.popup_error("Error al capturar video desde la cámara.")                 
                        window2.un_hide()
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
                
                frame==cv2.resize(fondoP2.copy(), P2camsize)
                imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                window2['-CAMARA-'].update(data=imgbytes)
            
        elif event == 'Escanear I':
            cap = cv2.VideoCapture(1)
            ret,img =cap.read()
            if not ret:
                window2.hide()
                sg.popup("no se detectó ninguna cámara")
                window2.un_hide()
                break
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
                    window2.hide()
                    sg.popup_error('Hoja no detectada, intente nuevamente',title='ERROR')
                    frame=cv2.rotate(imgContours.copy(), cv2.ROTATE_90_COUNTERCLOCKWISE)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2.un_hide()
                    window2['-CAMARA-'].update(data=imgbytes)
            else:
                window2.hide()
                #result=Manualconfig(uimage)
                if result is not None:
                    print("todo bien")
                    result=cv2.rotate(result.copy(), cv2.ROTATE_90_COUNTERCLOCKWISE)
                    imgbytes = cv2.imencode('.png', result)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
                window2.un_hide()
        elif event == 'Escanear D':
            cap = cv2.VideoCapture(0)
            ret,img =cap.read()
            if not ret:
                window2.hide()
                sg.popup("no se detectó ninguna cámara")
                window2.un_hide()
                break
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
                    window2.hide()
                    sg.popup_error('Hoja no detectada, intente nuevamente',title='ERROR')
                    frame=cv2.rotate(imgContours.copy(), cv2.ROTATE_90_CLOCKWISE)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    window2.un_hide()
                    window2['-CAMARA-'].update(data=imgbytes)
            else:
                window2.hide()
                #result=Manualconfig(uimage)
                if result is not None:
                    result=cv2.rotate(result.copy(), cv2.ROTATE_90_COUNTERCLOCKWISE)
                    imgbytes = cv2.imencode('.png', result)[1].tobytes()
                    window2['-CAMARA-'].update(data=imgbytes)
                window2.un_hide()
        elif event == 'salir de cámara':
            frame=fondoP2.copy()
            frame=cv2.resize(fondoP2.copy(), P2camsize)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window2['-CAMARA-'].update(data=imgbytes)
            
        elif event == '-TOGGLE-GRAPHIC-':  # if the graphical button that changes images
            window2['-TOGGLE-GRAPHIC-'].metadata = not window2['-TOGGLE-GRAPHIC-'].metadata
            window2['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_on if window2['-TOGGLE-GRAPHIC-'].metadata else toggle_btn_off)

            
            
        elif event == 'Imprimir':
            window2.hide()
            #WindowPrint()
            window2.un_hide()  
        elif event == 'Opciones Avanzadas':
            window2.hide()
            #Opciones()  
            window2.un_hide()  
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


top = [[sg.Text('BRAILLESCAN', size=(20, 1), justification='c', pad=(BPAD_TOP), font='Courier 30 bold')]]

block_3 = [[sg.Button('Empezar', size=(10, 2), font='Any 13')],
           [sg.Button('Apagar', size=(10, 2), font='Any 13')]]

block_2 = [[sg.Column([[sg.Button(image_data=fondoP2W, size=(9, 2), font='Any 8', key='-wifi-')]])]]

block_4 = [[sg.Image(data=fondo, size=Pf)]]

layout = [[sg.Column(top, size=(680, 60), pad=BPAD_TOP)],
          [sg.Column([[sg.Column(block_3, size=(150, 120), pad=BPAD_LEFT_INSIDE)],
                       [sg.Column(block_2, size=(160, 120), pad=BPAD_LEFT_INSIDE)]
                       ], background_color='#2b475d'),
           sg.Column(block_4, size=(540,400))]]

window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0, 0),
                   background_color='#2b475d', no_titlebar=True, grab_anywhere=True,size=(600,480))
b=False
while True:
    event1,value1=window.read()
    if event1 == 'Empezar'and b:
        window.hide()
        mainBsc()
        window.un_hide()
        b=False
    elif event1 == 'Empezar'and not b:
        window.hide()
        sg.popup("Primero debes comprobar la conexión a internet",title='ADVERTENCIA') 
        window.un_hide()    
    elif event1 == '-wifi-':
        b=True
        if comprobar_conexion():
            window.hide()
            sg.popup_ok("¡Estás conectado a Internet!",title='CONFIRMACIÓN')
            window.un_hide()
        else:
            # No hay conexión
            window.hide()
            sg.popup_error("No estás conectado a Internet",title='CONFIRMACIÓN')
            window.un_hide()
        #window.hide()
            wifiW()
        #window.un_hide()
    elif event1 == 'Apagar' or event1 == sg.WIN_CLOSED:
        window.hide()
        rsp=sg.popup_ok_cancel("El sistema se apagará de inmediato",title='ADVERTENCIA')
        if rsp == 'OK':
            print('apagar')
            os.system("sudo shutdown -h now")
            break
        else:
            window.un_hide()
window.close()
    

