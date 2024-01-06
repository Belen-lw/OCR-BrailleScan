import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import base64
from google.cloud import vision
import pytesseract
import platform
import unidecode
from autocorrect import Speller

import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2 import service_account

class Bordes:
    @staticmethod
    def preReqImg(uimage, bri, thrV):
        uimage = cv2.GaussianBlur(uimage, (45, 45), 3)
        ColorI = uimage.copy()
        uimage = cv2.cvtColor(uimage, cv2.COLOR_RGB2GRAY)
        imgBri = cv2.multiply(uimage, np.array([bri]))
        imgBri = cv2.GaussianBlur(imgBri, (45, 45), 3)
        _, thrI = cv2.threshold(imgBri, thrV, 255, cv2.THRESH_BINARY)
        return thrI

    @staticmethod
    def drawRectangle(img, biggest, thickness):
        cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
        cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
        cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
        cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
        return img

    @staticmethod
    def biggestContour(contours):
        biggest = np.array([])
        max_area = 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > 5000:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                if area > max_area and len(approx) == 4:
                    biggest = approx
                    max_area = area
        return biggest, max_area

    @staticmethod
    def reorder(myPoints):
        myPoints = myPoints.reshape((4, 2))
        myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] = myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew

    @staticmethod
    def Contorns(img, widthImg, heightImg, briF, threshold_value, remove_border=1):
        contI = Bordes.preReqImg(img, briF, threshold_value)
        imgContours = img.copy()
        imgBigContour = img.copy()
        contours, _ = cv2.findContours(contI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 2)
        
        biggest, _ = Bordes.biggestContour(contours)
        if biggest.size != 0:
            biggest = Bordes.reorder(biggest)
            cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)
            imgBigContour = Bordes.drawRectangle(imgBigContour, biggest, 2)
            pts1 = np.float32(biggest)
            pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
            imgWarpColored = imgWarpColored[remove_border:imgWarpColored.shape[0] - remove_border,
                             remove_border:imgWarpColored.shape[1] - remove_border]
            imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            return imgWarpGray, imgContours, imgBigContour
        else:
            return None, imgContours, None

class ImagetoText:
    def Tree_detect_text(image,pathT=None):
        sisOp = platform.system()
        if sisOp == "Windows":
            pytesseract.pytesseract.tesseract_cmd = pathT
        else: pass
        text=pytesseract.image_to_string(image, config='--psm 6 --oem 3',lang='spa')
        return text
    def GOO_detect_text(image,jsonfile):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] =jsonfile
        _, encoded_image = cv2.imencode('.jpg', image)
        img = base64.b64encode(encoded_image.tobytes()).decode('utf-8')
        client = vision.ImageAnnotatorClient()
        # with open(path, "rb") as image_file:
        #     content = image_file.read()
        image = vision.Image(content=img)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        ocr_text = []
        for text in texts:
            ocr_text.append(f"\r\n{text.description}")
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )
        return texts[0].description
    def M_corrector(word):
        spell = Speller(lang="es")
        corrected_word = spell(word)
        return corrected_word
    def A_corrector(txt,key):
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-pro")
        #print('model',model)
        resp=model.generate_content("arregla la ortofafia y gramatica de este texto y solo devuelveme el texto ignora la negrita de los titulos: "+txt)
        return (resp.text)
    def showProcess(imageArray, labels, Psize, rows, columns):
        num_images = len(imageArray)
        fig, axes = plt.subplots(rows, columns, figsize=(16, 8))
        
        for i in range(num_images):
            img = imageArray[i]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, Psize)
            imageArray[i] = img

        # Imprimir las imágenes y configurar etiquetas
        for i in range(rows):
            for j in range(columns):
                img_index = j + (i * columns)
                if img_index < num_images:
                    ax = axes[i][j]
                    img_to_show = imageArray[img_index]
                    label = labels[img_index]
                    ax.imshow(img_to_show, cmap='gray')
                    ax.set_title(label)
                    ax.axis('off')
        plt.tight_layout()
        plt.show()
    def texto_a_braille(texto):
        braille_dict = {
        'a': '100000',
        'b': '101000',
        'c': '110000',
        'd': '110100',
        'e': '100100',
        'f': '111000',
        'g': '111100',
        'h': '101100',
        'i': '011000',
        'j': '011100',
        'k': '100010',
        'l': '101010',
        'm': '110010',
        'n': '110110',
        'o': '100110',
        'p': '111010',
        'q': '111110',
        'r': '101110',
        's': '011010',
        't': '011110',
        'u': '100011',
        'v': '101011',
        'w': '011101',
        'x': '110011',
        'y': '110111',
        'z': '100111',
        'á': '001000',
        'é': '010110',
        'í': '011000',
        'ó': '010100',
        'ú': '011100',
        'ü': '100111',
        'ñ': '110110',
        '0': '001100',
        '1': '001000',
        '2': '001010',
        '3': '001110',
        '4': '001001',
        '5': '001101',
        '6': '001011',
        '7': '001111',
        '8': '001100',
        '9': '001100',
        ' ': '000000',
        ',': '010000',
        '.': '010110',
        '!': '011001',
        '?': '010010',
        ':': '010100',
        ';': '011100',
        '-': '010001',
        "'": '010011',
        '"': '010101',
        '(': '011011',
        ')': '011110',
        '/': '010111',
        '+': '011010',
        '=': '010111',
        '@': '011111',
        '#': '110001',
        '$': '110101',
        '%': '101001',
        '&': '111001',
        '*': '101101',
        '_': '011011',
        '|': '111101',
        '[': '111111',
        ']': '111110',
        '<': '101111',
        '>': '100001',
        '{': '101111',
        '}': '100001',
        '¡': '010011',
        '¿': '010010',
    }
        texto = unidecode.unidecode(texto.lower())
        resultado = ""
        ultimo_tipo = None

        for caracter in texto:
            if caracter in braille_dict:
                tipo_actual = 'letra' if caracter.isalpha() else 'numero'

                if ultimo_tipo is not None and tipo_actual != ultimo_tipo:
                    resultado += ' '

                resultado += braille_dict[caracter] + ' '
                ultimo_tipo = tipo_actual

        return resultado.strip()

    def text_to__braille_gcode(text, paperLimit=150):
        gcode_commands = []
        offsetX = 0
        offsetY = 0

        dot_positions = [
            (0, 0),
            (2.5, 0),
            (0, 2.5),
            (2.5, 2.5),
            (0, 5),
            (2.5, 5),
        ]

        for char in text:
            if (offsetX > paperLimit):
                offsetY += 10
                offsetX = 0
            braille_char = ImagetoText.texto_a_braille(char)
            for i, dot in enumerate(braille_char):
                if dot == '1':
                    dx, dy = dot_positions[i]
                    x = offsetX+dx
                    y = offsetY+dy
                    gcode_commands.append(f'G1 Y{y} X{x} F5000')
                    gcode_commands.append('M4 S100')
                    gcode_commands.append('M4 S0')
            offsetX += 7

        gcode_commands.append('M84')
        return gcode_commands

    def write_to_serial_port(ser, string_to_write):
            try:
                string_to_write = string_to_write + "\n"
                ser.write(string_to_write.encode())

                print(string_to_write)

            except Exception as e:
                print(f'Error: {str(e)}')
                    


        