import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
import threading


class SplashScreen:

    def __init__(self, image_path="img/loading.gif", duration=3):

        self.image_path = image_path
        self.duration = duration
        self.root = None
        self.gif = None
        self.frames = []
        self.current_frame = 0
        self.is_running = True

    def show(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        try:
            gif = Image.open(self.image_path)

            width, height = gif.size
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")

            frames = []
            try:
                for frame in ImageSequence.Iterator(gif):
                    frame = frame.convert('RGBA')
                    frames.append(ImageTk.PhotoImage(frame))
            except Exception as e:
                print(f"Error extracting frames: {e}")

            self.frames = frames

            if not self.frames:
                print("No frames found in GIF, creating static splash")
                self.create_static_splash(width, height)
            else:
                self.label = tk.Label(self.root, bg="black")
                self.label.pack(fill="both", expand=True)

                self.animate(0)

            threading.Thread(target=self.close_after_delay, daemon=True).start()

            self.root.mainloop()

        except Exception as e:
            print(f"Error loading splash image: {e}")
            self.is_running = False
            if self.root:
                try:
                    self.root.destroy()
                except:
                    pass

    def create_static_splash(self, width, height):
        frame = tk.Frame(self.root, width=width, height=height, bg="#212224")
        frame.pack(fill="both", expand=True)

        label = tk.Label(
            frame,
            text="Калькулятор загружается...",
            font=("Arial", 16, "bold"),
            fg="#FFFFFF",
            bg="#212224"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

    def on_close(self):
        self.is_running = False
        if hasattr(self, 'animation_id'):
            try:
                self.root.after_cancel(self.animation_id)
            except:
                pass
        self.root.destroy()

    def animate(self, counter):
        if not self.is_running or self.root is None:
            return

        if counter >= len(self.frames):
            counter = 0

        try:
            self.label.config(image=self.frames[counter])
            self.animation_id = self.root.after(100, self.animate, counter + 1)
        except Exception as e:
            print(f"Animation error: {e}")

    def close_after_delay(self):
        time.sleep(self.duration)
        self.is_running = False

        if self.root:
            try:
                if hasattr(self, 'animation_id'):
                    self.root.after_cancel(self.animation_id)
                self.root.after(0, self.root.destroy)
            except Exception as e:
                print(f"Error closing splash screen: {e}")