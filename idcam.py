import cv2

def test_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"La cámara {camera_index} no está disponible.")
        return False
    else:
        print(f"Cámara {camera_index} está disponible.")
        return True

def find_available_cameras(num_cameras=15):
    # Intentar abrir cámaras hasta el índice especificado
    for index in range(num_cameras):
        test_camera(index)

if __name__ == "__main__":
    find_available_cameras()