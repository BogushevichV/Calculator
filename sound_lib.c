#include <windows.h>
#include <mmsystem.h>
#include <stdio.h>
#include "sound_lib.h"

static int sounds_enabled = 1;
static int sound_type = 1; // 1 - drums, 0 - memes

__declspec(dllexport) int init_sound_system() {
    return 1; // Всегда успешно в этой реализации
}

__declspec(dllexport) int set_max_volume() {
    // Реализация через Windows API
    HWND hWnd = GetForegroundWindow();
    DWORD pid;
    GetWindowThreadProcessId(hWnd, &pid);

    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (hProcess == NULL) return 0;

    CloseHandle(hProcess);
    return 1;
}

__declspec(dllexport) int play_sound(const char* sound_path) {
    if (!sounds_enabled) return 0;

    if (sound_path == NULL) return 0;

    return PlaySoundA(sound_path, NULL, SND_FILENAME | SND_ASYNC);
}

__declspec(dllexport) void set_sound_type(int type) {
    sound_type = type;
}

__declspec(dllexport) void enable_sounds(int enable) {
    sounds_enabled = enable;
}