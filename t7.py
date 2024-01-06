
import cv2
import numpy as np
from ImageProcc import Bordes, ImagetoText

#threshold_type:  0 threshold_value:  118 kernel_size:  11 brillo_factor:  1.1
img = cv2.imread('img/FotoA_4.png')
imageCol = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
#PARAMS
#----------------------------------------------------------------------------------------------------------------------
heightImg = 1100
widthImg  = 790
threshold_value = 188
kernel_size = 3
brillo_factor = 1.6
threshold_type = cv2.THRESH_BINARY
a=41 #3
s=4 #5
height, width = img.shape[:2]
remove_border = 1 #remove pixels from border to avoid noise
th1=50
th2=150
keybar="AIzaSyCl3izNl0zJObfDxVpf30sGMl_uzaXGZ2g"
pathT='E:\\Tesseract-OCR\\tesseract'
jsonF='ocr-braillescan.json'
#pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract'
#to get Contours
#--------------------------------------------------------------------------------------------------------------------------------------------------
if width > height:
    #print(height,width)
    uimage =cv2.rotate(imageCol, cv2.ROTATE_90_COUNTERCLOCKWISE)
else:
    uimage=imageCol
    
imgWarpGray,imgContours,imgBigContour = Bordes.Contorns(uimage,widthImg, heightImg,brillo_factor,threshold_value)
#process to get text from image
#--------------------------------------------------------------------------------------------------------------------------------------
if imgWarpGray is not None or imgContours is not None or imgBigContour is not None:
    imageB = cv2.multiply(imgWarpGray, np.array([0.3]))
    i=cv2.adaptiveThreshold(imageB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, a, s)
    #i=cv2.adaptiveThreshold(imageB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, a, s)
    cv2.imwrite('scanned.png',i)
    cv2.imshow('result1',i)
    #-----------------------------------------------------------------------------------------------------------------------------------------
    #Show process
    imageArray = [uimage,imgContours,imgBigContour,imageB,imgWarpGray,i]
    lables = ["Original","Threshold","Contours","Warp gray","Warp Gray","Adaptive Threshold"]
    #cv2.imwrite('tot1.jpg', imgWarpGray)
    Psize = (800, 1000)
    rows,columns=2,3
    #plot
    #ImagetoText.showProcess(imageArray,lables,Psize,rows,columns)
    #cv2.imshow("Result2",i)
else:
    print("Bordes no detectados")
#----------------------------------------------------------------------------------------------------------------------
#text=ImagetoText.GOO_detect_text(i,jsonF)
#text =ImagetoText.Tree_detect_text(i,pathT) #psm --11
#textA=text.replace("\n", " ")   
#CorrectTextM=ImagetoText.M_corrector(textA)
#CorrectTextA=ImagetoText.A_corrector(text,keybar)
#print(text)
print('---------------------------AUTOMATIC CORRECTION------------------------------------')
#print(CorrectTextA)
print('----------------------------------MANUAL CORRECTION------------------------------------')
#print(CorrectTextM)
cv2.waitKey(0)
cv2.destroyAllWindows()