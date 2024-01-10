import cv2

def encender_camara(num_camara=2):
    cap = cv2.VideoCapture(num_camara)

    if not cap.isOpened():
        print(f"No se pudo abrir la cámara {num_camara}")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el fotograma")
            break

        cv2.imshow(f'Cámara {num_camara}', frame)

        # Presiona 'q' para salir del bucle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    encender_camara(2)
