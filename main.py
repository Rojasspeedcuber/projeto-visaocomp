
import cv2
import pygame
import sys
from pose_tracker import PoseTracker
from game_logic import Game

# Configurações
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def main():
    """Loop principal do jogo"""

    # Inicializa Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Body Motion Game - Desvie dos Obstáculos!")
    clock = pygame.time.Clock()

    # Inicializa câmera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    if not cap.isOpened():
        print("ERRO: Não foi possível abrir a câmera!")
        print("Verifique se sua webcam está conectada e funcionando.")
        sys.exit(1)

    # Inicializa rastreador de pose e jogo
    pose_tracker = PoseTracker()
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Flags
    show_camera = True
    running = True

    print("=" * 60)
    print("JOGO INICIADO - Body Motion Game")
    print("=" * 60)
    print("\nCamera ativada - Posicione-se em frente a webcam")
    print("\nCONTROLES:")
    print("  - Mover corpo lateralmente = Move personagem")
    print("  - Levantar bracos acima da cabeca = Pular")
    print("  - Agachar = Abaixar personagem")
    print("\nTECLAS:")
    print("  - D = Debug mode ON/OFF")
    print("  - C = Mostrar/Ocultar camera")
    print("  - R = Reiniciar (Game Over)")
    print("  - Q/ESC = Sair")
    print("\n" + "=" * 60)

    # Loop principal
    while running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Sair
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

                # Toggle debug
                elif event.key == pygame.K_d:
                    game.toggle_debug()
                    print(f"Debug mode: {'ON' if game.debug_mode else 'OFF'}")

                # Toggle câmera
                elif event.key == pygame.K_c:
                    show_camera = not show_camera
                    print(f"Câmera overlay: {'ON' if show_camera else 'OFF'}")

                # Reiniciar
                elif event.key == pygame.K_r and game.state == 'game_over':
                    game.restart()
                    print("[INFO] Jogo reiniciado!")

        # Captura frame da câmera
        ret, frame = cap.read()
        if not ret:
            print("ERRO: Não foi possível ler frame da câmera")
            break

        # Espelha horizontalmente para ficar intuitivo
        frame = cv2.flip(frame, 1)

        # Processa pose
        results = pose_tracker.process_frame(frame)

        # Calibração inicial
        if not pose_tracker.is_calibrated:
            pose_tracker.calibrate(results)
        else:
            pose_tracker.detect_movement(results)

        # Desenha landmarks no frame
        if show_camera or game.debug_mode:
            frame_with_pose = pose_tracker.draw_landmarks(frame.copy(), results)
        else:
            frame_with_pose = None

        # Obtém estado da pose
        pose_state = pose_tracker.get_state()

        # Atualiza jogo
        game.update(pose_state)

        # Desenha jogo
        game.draw(screen, frame_with_pose if show_camera else None, pose_state)

        # Mostra janela da câmera separada (debug)
        if game.debug_mode and results.pose_landmarks:
            debug_frame = pose_tracker.draw_landmarks(frame.copy(), results)

            # Adiciona info na janela
            cv2.putText(debug_frame, f"X: {pose_state['x_position']:.2f}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Jump: {pose_state['is_jumping']}",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Crouch: {pose_state['is_crouching']}",
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Debug - Pose Detection', debug_frame)
            cv2.waitKey(1)

        # Atualiza display
        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

    print("\n" + "=" * 60)
    print(f"Jogo encerrado - Pontuacao final: {game.score}")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
