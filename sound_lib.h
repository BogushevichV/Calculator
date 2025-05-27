#ifndef SOUND_LIB_H
#define SOUND_LIB_H

#ifdef __cplusplus
extern "C" {
#endif

// Инициализация звуковой системы
__declspec(dllexport) int init_sound_system();

// Установка максимальной громкости
__declspec(dllexport) int set_max_volume();

// Воспроизведение звука
__declspec(dllexport) int play_sound(const char* sound_path);

// Установка типа звуков (1 - барабаны, 0 - мемы)
__declspec(dllexport) void set_sound_type(int type);

// Включение/выключение звуков
__declspec(dllexport) void enable_sounds(int enable);

#ifdef __cplusplus
}
#endif

#endif // SOUND_LIB_H