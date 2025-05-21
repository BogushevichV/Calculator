import tkinter as tk
import os
import sys
from SplashScreen import SplashScreen
from Controller import CalculatorController
from VergilPortal import VergilPortal


def on_closing(root):
    exit_video_path = "img/Vergil Portal.mp4"
    exit_audio_path = "img/Vergil Portal.mp3"
    if os.path.exists(exit_video_path):
        vergil_portal = VergilPortal(exit_video_path, exit_audio_path)
        vergil_portal.show()
        root.after(18000, root.destroy)  # Задержка 1 секунда перед закрытием
    else:
        root.destroy()


if __name__ == "__main__":
    try:
        gif_path = "img/loading.gif"
        if os.path.exists(gif_path):
            splash = SplashScreen(gif_path, duration=3)
            splash.show()

            root = tk.Tk()
        else:
            root = tk.Tk()

        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

        app = CalculatorController(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
