import cv2
import mediapipe as mp
import math
from pynput.keyboard import Controller, Key

mp_dibujo = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
teclado = Controller()

captura = cv2.VideoCapture(0, cv2.CAP_DSHOW)

tecla_c_presionada = False
tecla_v_presionada = False

MANO_LEVANTADA = 150
MANO_LEVANTADA2 = 300

with mp_pose.Pose(static_image_mode=False) as pose:
    while True:
        ret, marco = captura.read()
        if not ret:
            break

        marco = cv2.flip(marco, 1)
        altura, ancho, _ = marco.shape
        marco_rgb = cv2.cvtColor(marco, cv2.COLOR_BGR2RGB)

        resultados = pose.process(marco_rgb)

        if resultados.pose_landmarks:
            mp_dibujo.draw_landmarks(
                marco, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_dibujo.DrawingSpec(color=(128, 0, 250), thickness=2, circle_radius=3),
                mp_dibujo.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            muneca_derecha = resultados.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            muneca_izquierda = resultados.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]

            muneca_derecha_y = int(muneca_derecha.y * altura)
            muneca_izquierda_y = int(muneca_izquierda.y * altura)

            if muneca_derecha_y < MANO_LEVANTADA2 or muneca_izquierda_y < MANO_LEVANTADA2:
                if not tecla_c_presionada:
                    teclado.press('c')
                    tecla_c_presionada = True
            else:
                if tecla_c_presionada:
                    teclado.release('c')
                    tecla_c_presionada = False

            muneca_derecha_x = int(muneca_derecha.x * ancho)
            muneca_izquierda_x = int(muneca_izquierda.x * ancho)
            cv2.line(marco, 
                    (muneca_derecha_x, muneca_derecha_y), 
                    (muneca_izquierda_x, muneca_izquierda_y), 
                    (0, 255, 0), 3)

            angulo_radianes = math.atan2(muneca_izquierda_y - muneca_derecha_y, 
                                        muneca_izquierda_x - muneca_derecha_x)
            angulo_grados = math.degrees(angulo_radianes)

            if 20 <= angulo_grados <= 100:
                teclado.press(Key.right)
            else:
                teclado.release(Key.right)

            if -100 <= angulo_grados <= -20:
                teclado.press(Key.left)
            else:
                teclado.release(Key.left)

            cv2.putText(marco, f"Angulo: {angulo_grados:.2f} grados", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.circle(marco, (muneca_derecha_x, muneca_derecha_y), 5, (0, 0, 255), -1)
            cv2.circle(marco, (muneca_izquierda_x, muneca_izquierda_y), 5, (0, 0, 255), -1)

            if (muneca_derecha_y < MANO_LEVANTADA or muneca_izquierda_y < MANO_LEVANTADA):
                if not tecla_v_presionada:
                    teclado.press('v')
                    tecla_v_presionada = True
            else:
                if tecla_v_presionada:
                    teclado.release('v')
                    tecla_v_presionada = False

        cv2.imshow("Mediapipe", marco)

        if cv2.waitKey(1) & 0xFF == 27:
            break

captura.release()
cv2.destroyAllWindows()

