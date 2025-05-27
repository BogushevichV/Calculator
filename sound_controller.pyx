import random
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import winsound

cdef class SoundController:
    cdef object volume
    cdef list drums_sounds
    cdef list mem_sounds
    cdef list selected_sounds
    cdef bint sounds_enabled
    cdef str sound_type

    def __cinit__(self, drums_sounds, mem_sounds, enabled=True, sound_type="drums"):
        self.drums_sounds = drums_sounds
        self.mem_sounds = mem_sounds
        self.sounds_enabled = enabled
        self.sound_type = sound_type
        self.selected_sounds = drums_sounds if sound_type == "drums" else mem_sounds

        # Инициализация аудиоинтерфейса
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    cpdef set_max_volume(self):
        """Устанавливает максимальную громкость"""
        try:
            if self.volume.GetMute():
                self.volume.SetMute(False, None)
            self.volume.SetMasterVolumeLevelScalar(1.0, None)
            return True
        except Exception as e:
            print(f"Ошибка установки громкости: {e}")
            return False

    cpdef play_button_sound(self):
        """Воспроизводит случайный звук"""
        if not self.sounds_enabled:
            return False

        try:
            self.set_max_volume()
            sound_file = random.choice(self.selected_sounds)
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
            return False

    cpdef set_sound_type(self, str sound_type):
        """Устанавливает тип звуков"""
        self.sound_type = sound_type
        self.selected_sounds = self.drums_sounds if sound_type == "drums" else self.mem_sounds

    cpdef set_sounds_enabled(self, bint enabled):
        """Включает/выключает звуки"""
        self.sounds_enabled = enabled

    cpdef get_status(self):
        """Возвращает текущие настройки звуков"""
        return {
            "enabled": self.sounds_enabled,
            "type": self.sound_type
        }