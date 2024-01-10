import cv2

# Inicializa la cámara
cap = cv2.VideoCapture(2)

nueva_anchura = 1080
nueva_altura = 720
num_foto = 1

while num_foto <= 15:
    # Captura un cuadro de la cámara
    ret, frame = cap.read()

    # Redimensiona el cuadro al tamaño deseado
    frame = cv2.resize(frame, (nueva_anchura, nueva_altura))

    # Muestra el cuadro en una ventana
    cv2.imshow('Camara', frame)

    # Espera la tecla "Espacio" para tomar una foto
    key = cv2.waitKey(1)
    if key == 32:  # 32 es el código ASCII para la tecla "Espacio"
        nombre_archivo = f'img/FotoC_{num_foto}.png'
        cv2.imwrite(nombre_archivo, frame)
        print(f'Foto tomada: {nombre_archivo}')
        num_foto += 1
    if key == 27:
        break

# Libera la cámara y cierra la ventana
cap.release()
cv2.destroyAllWindows()
