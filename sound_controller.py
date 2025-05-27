import os
import random
import ctypes
from ctypes import c_int, c_char_p


class SoundController:
    def __init__(self, drums_sounds, mem_sounds, enabled=True, sound_type="drums"):
        # Загрузка DLL
        self.lib = ctypes.WinDLL(os.path.abspath("sound_lib.dll"))

        # Определение типов аргументов и возвращаемых значений
        self.lib.init_sound_system.restype = c_int
        self.lib.set_max_volume.restype = c_int
        self.lib.play_sound.argtypes = [c_char_p]
        self.lib.play_sound.restype = c_int
        self.lib.set_sound_type.argtypes = [c_int]
        self.lib.enable_sounds.argtypes = [c_int]

        # Инициализация
        self.drums_sounds = [s.encode('utf-8') for s in drums_sounds]
        self.mem_sounds = [s.encode('utf-8') for s in mem_sounds]
        self.sounds_enabled = enabled
        self.sound_type = 1 if sound_type == "drums" else 0
        self.selected_sounds = self.drums_sounds if self.sound_type else self.mem_sounds

        self.lib.init_sound_system()
        self.lib.enable_sounds(1 if enabled else 0)
        self.lib.set_sound_type(self.sound_type)

    def set_max_volume(self):
        return bool(self.lib.set_max_volume())

    def play_button_sound(self):
        if not self.sounds_enabled:
            return False

        sound_file = random.choice(self.selected_sounds)
        return bool(self.lib.play_sound(sound_file))

    def set_sound_type(self, sound_type):
        self.sound_type = 1 if sound_type == "drums" else 0
        self.selected_sounds = self.drums_sounds if self.sound_type else self.mem_sounds
        self.lib.set_sound_type(self.sound_type)

    def set_sounds_enabled(self, enabled):
        self.sounds_enabled = enabled
        self.lib.enable_sounds(1 if enabled else 0)

    def get_status(self):
        return {
            "enabled": self.sounds_enabled,
            "type": "drums" if self.sound_type else "memes"
        }