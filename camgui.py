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
        while True:
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
        #sg.popup('Button B pressed!')
        cap = cv2.VideoCapture(1)
        capturar_video(cap,window2)
        frame=cv2.resize(fondoP2.copy(), P2camsize)
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