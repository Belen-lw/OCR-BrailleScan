import cv2

# Abre la cámara
cap = cv2.VideoCapture(0)

while True:
    # Lee el cuadro desde la cámara
    ret, frame = cap.read()

    # Muestra el cuadro en una ventana
    cv2.imshow('Camara en Vivo', frame)

    # Rompe el bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la cámara y cierra la ventana
cap.release()
cv2.destroyAllWindows()
