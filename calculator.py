import tkinter as tk
import os
import sys
import json
from SplashScreen import SplashScreen
from Controller import CalculatorController
from VergilPortal import VergilPortal

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

gif_path = config['paths']['loading_gif']
exit_video_path = config['paths']['vergil_video']
exit_audio_path = config['paths']['vergil_audio']


def on_closing(root):
    if os.path.exists(exit_video_path) & os.path.exists(exit_audio_path):
        vergil_portal = VergilPortal(exit_video_path, exit_audio_path)
        vergil_portal.show()
        root.after(18000, root.destroy)  # Задержка 1 секунда перед закрытием
    else:
        root.destroy()


if __name__ == "__main__":
    try:
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
