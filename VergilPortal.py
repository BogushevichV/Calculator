import cv2
import pygame
import threading


class VergilPortal:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.is_showing = False

    def show(self):
        if self.is_showing:
            return

        self.is_showing = True
        thread = threading.Thread(target=self._play_video_with_sound, daemon=True)
        thread.start()

    def _play_video_with_sound(self):
        # Инициализация Pygame для звука
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_path)  # Поддерживает MP3, WAV, OGG

        # Загрузка видео через OpenCV
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Создаем окно OpenCV
        cv2.namedWindow("Vergil Portal", cv2.WINDOW_NORMAL)
        pygame.mixer.music.play()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Показываем кадр
            cv2.imshow("Vergil Portal", frame)
            # Выход по нажатию 'q' или закрытию окна
            if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
                break

        # Освобождаем ресурсы
        cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.music.stop()