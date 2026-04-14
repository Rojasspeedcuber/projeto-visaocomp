import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class PoseTracker:
    """Detecta e rastreia a pose corporal usando MediaPipe"""

    def __init__(self):
        # Configurações do detector de pose
        base_options = python.BaseOptions(model_asset_path=self._download_model())
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

        # Estado do jogador
        self.x_position = 0.5  # Posição normalizada (0-1)
        self.is_jumping = False
        self.is_crouching = False

        # Calibração inicial
        self.calibration_samples = []
        self.is_calibrated = False
        self.baseline_shoulder_y = None
        self.baseline_hip_y = None

        # Último resultado para desenho
        self.last_result = None
        self.frame_timestamp_ms = 0

    def _download_model(self):
        """Baixa o modelo de pose se necessário"""
        import urllib.request
        import os

        model_path = 'pose_landmarker_lite.task'
        expected_size = 4000000  # ~4MB (modelo lite)

        # Verifica se arquivo existe e tem tamanho válido
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            if file_size > expected_size:
                return model_path
            else:
                print("[AVISO] Arquivo corrompido detectado. Baixando novamente...")
                os.remove(model_path)

        print("[INFO] Baixando modelo de pose do MediaPipe (~10MB)...")
        url = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'

        try:
            # Download com verificação
            urllib.request.urlretrieve(url, model_path)

            # Verifica se download foi bem-sucedido
            if os.path.exists(model_path) and os.path.getsize(model_path) > expected_size:
                print("[OK] Modelo baixado com sucesso!")
                return model_path
            else:
                raise Exception("Download incompleto")

        except Exception as e:
            print(f"[ERRO] Falha no download: {e}")
            print("[INFO] Tente baixar manualmente de:")
            print(url)
            if os.path.exists(model_path):
                os.remove(model_path)
            raise

        return model_path

    def process_frame(self, frame):
        """Processa frame e retorna landmarks"""
        # Converte para formato RGB do MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Detecta pose
        self.frame_timestamp_ms += 33  # ~30 FPS
        result = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)

        self.last_result = result
        return result

    def draw_landmarks(self, frame, results):
        """Desenha esqueleto do corpo no frame"""
        if not results or not results.pose_landmarks:
            return frame

        # Converte landmarks para formato compatível
        for pose_landmarks in results.pose_landmarks:
            # Desenha conexões
            h, w = frame.shape[:2]

            # Desenha pontos
            for landmark in pose_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            # Desenha conexões básicas
            connections = [
                (11, 12), (12, 14), (14, 16),  # Braço direito
                (11, 13), (13, 15),  # Braço esquerdo
                (11, 23), (12, 24),  # Tronco
                (23, 24), (23, 25), (24, 26),  # Quadril e pernas
                (25, 27), (26, 28),  # Pernas inferiores
            ]

            for start, end in connections:
                if start < len(pose_landmarks) and end < len(pose_landmarks):
                    start_point = (int(pose_landmarks[start].x * w), int(pose_landmarks[start].y * h))
                    end_point = (int(pose_landmarks[end].x * w), int(pose_landmarks[end].y * h))
                    cv2.line(frame, start_point, end_point, (0, 0, 255), 2)

        return frame

    def calibrate(self, results):
        """Calibra posição base do usuário"""
        if not results or not results.pose_landmarks:
            return False

        landmarks = results.pose_landmarks[0]

        # Média dos ombros e quadris
        shoulder_y = (landmarks[11].y + landmarks[12].y) / 2  # LEFT_SHOULDER, RIGHT_SHOULDER
        hip_y = (landmarks[23].y + landmarks[24].y) / 2  # LEFT_HIP, RIGHT_HIP

        self.calibration_samples.append((shoulder_y, hip_y))

        # Calibra após 30 amostras
        if len(self.calibration_samples) >= 30:
            shoulders = [s[0] for s in self.calibration_samples]
            hips = [s[1] for s in self.calibration_samples]

            self.baseline_shoulder_y = np.mean(shoulders)
            self.baseline_hip_y = np.mean(hips)
            self.is_calibrated = True
            return True

        return False

    def detect_movement(self, results):
        """Detecta movimentos corporais e atualiza estado"""
        if not results or not results.pose_landmarks or not self.is_calibrated:
            return

        landmarks = results.pose_landmarks[0]

        # 1. Movimento Lateral (baseado no centro dos ombros)
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]

        # Centro do corpo
        center_x = (left_shoulder.x + right_shoulder.x) / 2
        self.x_position = center_x  # Normalizado 0-1

        # 2. Pulo (braços levantados acima da cabeça)
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]

        # Se ambas as mãos estão acima dos ombros
        avg_wrist_y = (left_wrist.y + right_wrist.y) / 2
        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

        self.is_jumping = avg_wrist_y < avg_shoulder_y - 0.1

        # 3. Agachar (joelhos flexionados)
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        avg_hip_y = (left_hip.y + right_hip.y) / 2

        # Se o quadril está mais baixo que o normal
        self.is_crouching = avg_hip_y > self.baseline_hip_y + 0.08

    def get_state(self):
        """Retorna estado atual do jogador"""
        return {
            'x_position': self.x_position,
            'is_jumping': self.is_jumping,
            'is_crouching': self.is_crouching,
            'is_calibrated': self.is_calibrated,
            'calibration_progress': len(self.calibration_samples) / 30.0
        }

    def reset_calibration(self):
        """Reseta calibração"""
        self.calibration_samples = []
        self.is_calibrated = False
        self.baseline_shoulder_y = None
        self.baseline_hip_y = None
