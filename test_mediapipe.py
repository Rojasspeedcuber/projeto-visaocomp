"""Script de teste para verificar se MediaPipe está funcionando"""
import cv2
import sys

print("Testando imports...")

try:
    import mediapipe as mp
    print(f"[OK] MediaPipe {mp.__version__} importado")
except Exception as e:
    print(f"[ERRO] MediaPipe: {e}")
    sys.exit(1)

try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    print("[OK] MediaPipe tasks importado")
except Exception as e:
    print(f"[ERRO] MediaPipe tasks: {e}")
    sys.exit(1)

try:
    import pygame
    print(f"[OK] Pygame importado")
except Exception as e:
    print(f"[ERRO] Pygame: {e}")
    sys.exit(1)

print("\nTestando criacao do PoseTracker...")

try:
    from pose_tracker import PoseTracker
    print("[INFO] Criando PoseTracker (pode demorar se precisar baixar modelo)...")
    tracker = PoseTracker()
    print("[OK] PoseTracker criado com sucesso!")
    print(f"[INFO] Modelo carregado: pose_landmarker_lite.task")
except Exception as e:
    print(f"[ERRO] PoseTracker: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("TODOS OS TESTES PASSARAM!")
print("O jogo esta pronto para ser executado.")
print("="*60)
print("\nExecute: python main.py")
