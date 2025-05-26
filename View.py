import random
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import winsound
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import math
import sys
from ConfigManager import ConfigManager


class CalculatorView:
    """Представление калькулятора - отвечает за отображение интерфейса"""

    def __init__(self, root, controller, history_options, options, buttons, decorator_options=None, sound_options=None):
        self.root = root
        self.controller = controller

        # Инициализация ConfigManager
        self.config = ConfigManager()

        self.buttons = None
        self.scrollbar = None
        self.img = None
        self.entry = None
        self.entry_frame = None

        # Получение параметров шрифтов из конфига
        self.base_font_size = self.config.get("ui", "fonts", "base_font_size")
        self.entry_font_size = self.config.get("ui", "fonts", "entry_font_size")
        self.options_font_size = self.config.get("ui", "fonts", "options_font_size")

        # Получение параметров окна из конфига
        self.initial_width = self.config.get("ui", "window", "initial_width")
        self.initial_height = self.config.get("ui", "window", "initial_height")

        self.scale_factor = 1

        self.history_options = history_options
        self.options = options
        self.buttons = buttons
        self.decorator_options = decorator_options
        self.sound_options = sound_options or {"Звуки включены":
                                                   self.config.get("sounds", "default_options", "enabled"),
                                               "Тип звука": self.config.get("sounds", "default_options", "type")}

        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        # Получение списков звуков из конфига
        self.mem_sounds = self.config.get("sounds", "files", "memes")
        self.drums_sounds = self.config.get("sounds", "files", "drums")

        # Определение выбранных звуков на основе настроек
        self.selected_sounds = self.drums_sounds if (
                self.sound_options["Тип звука"] == self.config.get("sounds", "default_options", "type")) \
            else self.mem_sounds

        # Настройка окна
        window_title = self.config.get("ui", "window", "title")
        window_bg = self.config.get("ui", "window", "background_color")
        icon_path = self.config.get("ui", "window", "icon_path")

        self.root.title(window_title)
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")
        self.root.configure(bg=window_bg)

        img = Image.open(icon_path)
        photo = ImageTk.PhotoImage(img)
        self.root.iconphoto(False, photo)
        self.root.bind("<Configure>", self.on_window_resize)

        # Настройка курсора
        self.setup_cursor()

        self.all_buttons = []
        self.history_option_widgets = []
        self.option_checkbuttons = []
        self.decorator_option_widgets = []
        self.sound_option_widgets = []

        # Создаем главное меню вместо отдельных опций
        self.create_menu_bar()

        self.create_widgets()
        self.update_buttons(self.options, self.buttons)
        self.setup_layout()

        # Создаем статусную строку для вывода информации о времени выполнения и т.д.
        self.status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=30)
        status_bar_row = self.config.get("grid_layout", "status_bar_row")
        self.status_bar.grid(row=status_bar_row, column=0, columnspan=10, sticky="nsew")

    def setup_cursor(self):
        """Настройка курсора на основе конфигурации"""
        try:
            cursor_config = self.config.get("ui", "cursors", "custom_cursor")
            if cursor_config.get("enabled"):
                cursor_path = cursor_config.get("path")
                cursor_size = cursor_config.get("size")
                temp_file = cursor_config.get("temp_file")

                # Загрузка изображения курсора
                cursor_img = Image.open(cursor_path)
                cursor_img = cursor_img.resize(cursor_size, Image.Resampling.LANCZOS)

                # Создание курсора (только для Windows)
                if sys.platform == 'win32':
                    from ctypes import windll, create_string_buffer

                    # Конвертируем изображение в формат .cur
                    cursor_img.save(temp_file, format="ICO")

                    # Загружаем курсор
                    h_cursor = windll.user32.LoadImageW(
                        0, temp_file, 2, 0, 0, 0x00000010
                    )
                    cursor = f"@{temp_file}"
                    self.root.config(cursor=cursor)
                else:
                    # Для других ОС используем стандартный курсор
                    default_cursor = self.config.get("ui", "cursors", "default")
                    self.root.config(cursor=default_cursor)
            else:
                default_cursor = self.config.get("ui", "cursors", "default")
                self.root.config(cursor=default_cursor)

        except Exception as e:
            print(f"Ошибка загрузки курсора: {e}")
            default_cursor = self.config.get("ui", "cursors", "default")
            self.root.config(cursor=default_cursor)

    def on_window_resize(self, event):
        """Обработчик изменения размера окна"""
        if event.widget == self.root:
            # Получаем текущие размеры окна
            width = self.root.winfo_width()
            height = self.root.winfo_height()

            # Вычисляем коэффициенты масштабирования
            width_scale = width / self.initial_width
            height_scale = height / self.initial_height

            self.scale_factor = math.sqrt(width_scale * height_scale)

            # Получаем ограничения масштабирования из конфига
            min_scale = self.config.get("ui", "scaling", "min_scale_factor")
            max_scale = self.config.get("ui", "scaling", "max_scale_factor")
            self.scale_factor = max(min_scale, min(self.scale_factor, max_scale))

            # Обновляем размер шрифта для всех элементов
            self.update_font_sizes()

    def set_max_volume(self):
        """Устанавливает максимальную громкость"""
        try:
            volume_config = self.config.get("sounds", "volume")

            if volume_config.get("unmute_on_play") and self.volume.GetMute():
                self.volume.SetMute(False, None)

            if volume_config.get("auto_max_volume"):
                self.volume.SetMasterVolumeLevelScalar(1.0, None)
        except Exception as e:
            print(f"Ошибка установки громкости: {e}")

    def play_button_sound(self):
        """Воспроизводит случайный звук при нажатии кнопки"""
        sounds_enabled = self.sound_options.get("Звуки включены",
                                                self.config.get("sounds", "default_options", "enabled"))
        if not sounds_enabled:
            return

        try:
            self.set_max_volume()
            sound_file = random.choice(self.selected_sounds)
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

    def update_font_sizes(self):
        """Обновляет размеры шрифтов для всех элементов интерфейса"""
        # Получение настроек шрифтов из конфига
        button_font_family = self.config.get("ui", "fonts", "button_font", "family")
        button_font_weight = self.config.get("ui", "fonts", "button_font", "weight")
        entry_font_family = self.config.get("ui", "fonts", "entry_font", "family")

        # Обновляем шрифт кнопок
        new_button_font = (button_font_family, int(self.base_font_size * self.scale_factor), button_font_weight)
        for button in self.all_buttons:
            button.config(font=new_button_font)

        # Обновляем шрифт поля ввода
        new_entry_font = (entry_font_family, int(self.entry_font_size * self.scale_factor))
        self.entry.config(font=new_entry_font)

        # Обновляем шрифт чекбоксов
        new_option_font = (entry_font_family, int(self.options_font_size * self.scale_factor))
        for chk in self.option_checkbuttons:
            chk.config(font=new_option_font)

        for widget in self.history_option_widgets:
            widget.config(font=new_option_font)

        for widget in self.decorator_option_widgets:
            widget.config(font=new_option_font)

        for widget in self.sound_option_widgets:
            widget.config(font=new_option_font)

    def create_menu_bar(self):
        """Создает верхнее меню для всех опций"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Получение меток меню из конфига
        menu_labels = self.config.get("menu", "labels")
        history_items = self.config.get("menu", "history_items")
        decorator_items = self.config.get("menu", "decorator_items")
        sound_items = self.config.get("menu", "sound_items")
        view_items = self.config.get("menu", "view_items")

        # Создаем меню функций
        self.functions_menu = tk.Menu(self.menu_bar, tearoff=0, )
        self.menu_bar.add_cascade(label=menu_labels.get("functions"), menu=self.functions_menu)

        # Создаем переменные для хранения состояний опций
        self.options_vars = {
            key: tk.BooleanVar(value=val) for key, val in self.options.items()
        }

        # Добавляем элементы в меню функций
        for option, var in self.options_vars.items():
            self.functions_menu.add_checkbutton(
                label=option,
                variable=var,
                command=self.update_functionality
            )

        # Создаем меню истории
        self.history_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=menu_labels.get("history"), menu=self.history_menu)

        # Создаем переменные для хранения настроек истории
        self.history_options_vars = {
            "Сохранение выражений": tk.BooleanVar(value=self.history_options["Сохранение выражений"]),
            "Лимит истории": tk.IntVar(value=self.history_options["Лимит истории"]),
            "Путь файла": tk.StringVar(value=self.history_options["Путь файла"]),
        }

        # Добавляем элементы в меню истории
        self.history_menu.add_checkbutton(
            label=history_items.get("save_expressions"),
            variable=self.history_options_vars["Сохранение выражений"],
            command=self.update_functionality
        )
        self.history_menu.add_command(
            label=history_items.get("change_limit"),
            command=self.controller.change_history_limit
        )
        self.history_menu.add_command(
            label=history_items.get("change_path"),
            command=self.controller.change_history_path
        )
        self.history_menu.add_separator()
        self.history_menu.add_command(
            label=history_items.get("show_history"),
            command=lambda: self.controller.show_history()
        )

        # Создаем меню декораторов
        self.decorator_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=menu_labels.get("decorators"), menu=self.decorator_menu)

        # Создаем переменные для хранения настроек декораторов
        self.decorator_options_vars = {
            key: tk.BooleanVar(value=val) for key, val in self.decorator_options.items()
        }

        # Добавляем элементы в меню декораторов
        for option, var in self.decorator_options_vars.items():
            self.decorator_menu.add_checkbutton(
                label=option,
                variable=var,
                command=self.update_decorator_functionality
            )

        # Добавляем специальные команды для декораторов
        self.decorator_menu.add_separator()
        self.decorator_menu.add_command(
            label=decorator_items.get("change_precision"),
            command=self.controller.change_precision
        )

        # Создаем меню звуков
        self.sound_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=menu_labels.get("sounds"), menu=self.sound_menu)

        # Создаем переменные для хранения настроек звуков
        default_sound_enabled = self.config.get("sounds", "default_options", "enabled")
        default_sound_type = self.config.get("sounds", "default_options", "type")

        self.sound_options_vars = {
            "Звуки включены": tk.BooleanVar(value=self.sound_options.get("Звуки включены", default_sound_enabled)),
            "Тип звука": tk.StringVar(value=self.sound_options.get("Тип звука", default_sound_type))
        }

        # Добавляем элементы в меню звуков
        self.sound_menu.add_checkbutton(
            label=sound_items.get("sounds_enabled"),
            variable=self.sound_options_vars["Звуки включены"],
            command=self.update_sound_functionality
        )

        self.sound_menu.add_separator()

        # Добавляем выбор типа звука
        sound_type_menu = tk.Menu(self.sound_menu, tearoff=0)
        self.sound_menu.add_cascade(label=sound_items.get("sound_type"), menu=sound_type_menu)

        sound_type_menu.add_radiobutton(
            label=sound_items.get("drums"),
            variable=self.sound_options_vars["Тип звука"],
            value="drums",
            command=self.update_sound_type
        )
        sound_type_menu.add_radiobutton(
            label=sound_items.get("memes"),
            variable=self.sound_options_vars["Тип звука"],
            value="memes",
            command=self.update_sound_type
        )

        # Добавляем меню "Вид" для управления интерфейсом
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=menu_labels.get("view"), menu=self.view_menu)

        # Добавляем переменную для переключения панели опций
        self.show_options_panel = tk.BooleanVar(value=False)
        self.view_menu.add_checkbutton(
            label=view_items.get("show_options_panel"),
            variable=self.show_options_panel,
            command=self.toggle_options_panel
        )

        # Создаем скрытую панель для опций
        self.create_options_panel()

    def create_options_panel(self):
        """Создает панель опций, которая будет скрыта/показана по запросу"""
        # Получение цветов из конфига
        background_color = self.config.get("ui", "colors", "background")
        frame_bg = self.config.get("ui", "colors", "frame_background")
        frame_fg = self.config.get("ui", "colors", "frame_foreground")
        selectcolor = self.config.get("ui", "colors", "selectcolor")
        activebackground = self.config.get("ui", "colors", "activebackground")
        button_default = self.config.get("ui", "colors", "button_default")

        options_panel_row = self.config.get("grid_layout", "options_panel_row")

        self.options_panel = tk.Frame(self.root, bg=background_color)
        self.options_panel.grid(row=options_panel_row, column=0, columnspan=10, sticky="nsew")
        self.options_panel.grid_remove()  # Скрываем панель по умолчанию

        # Панель функций
        functions_frame = tk.LabelFrame(self.options_panel, text="Функции", fg=frame_fg, bg=frame_bg)
        functions_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        row = 0
        for option, var in self.options_vars.items():
            chk = tk.Checkbutton(
                functions_frame, text=option, variable=var,
                command=self.update_functionality, cursor=self.config.get("ui", "cursors", "checkbox"),
                bg=frame_bg, fg=frame_fg,
                selectcolor=selectcolor, activebackground=activebackground
            )
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            self.option_checkbuttons.append(chk)
            row += 1

        # Панель истории
        history_frame = tk.LabelFrame(self.options_panel, text="История", fg=frame_fg, bg=frame_bg)
        history_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Сохранение выражений
        chk = tk.Checkbutton(
            history_frame, text="Сохранение выражений",
            variable=self.history_options_vars["Сохранение выражений"],
            command=self.update_functionality, bg=frame_bg, fg=frame_fg,
            selectcolor=selectcolor, activebackground=activebackground,
            cursor=self.config.get("ui", "cursors", "checkbox")
        )
        chk.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(chk)

        # Лимит истории
        btn = tk.Button(
            history_frame, text="Изменить лимит истории",
            command=self.controller.change_history_limit,
            bg=button_default, fg=frame_fg, cursor=self.config.get("ui", "cursors", "button")
        )
        btn.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(btn)

        # Путь к файлу
        btn = tk.Button(
            history_frame, text="Изменить путь файла истории",
            command=self.controller.change_history_path,
            bg=button_default, fg=frame_fg, cursor=self.config.get("ui", "cursors", "button")
        )
        btn.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(btn)

        # Панель декораторов
        decorator_frame = tk.LabelFrame(self.options_panel, text="Декораторы", fg=frame_fg, bg=frame_bg)
        decorator_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        row = 0
        for option, var in self.decorator_options_vars.items():
            chk = tk.Checkbutton(
                decorator_frame, text=option,
                variable=var,
                command=self.update_decorator_functionality,
                bg=frame_bg, fg=frame_fg, selectcolor=selectcolor,
                activebackground=activebackground, cursor=self.config.get("ui", "cursors", "checkbox")
            )
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            self.decorator_option_widgets.append(chk)
            row += 1

        # Кнопка точности
        btn = tk.Button(
            decorator_frame, text="Изменить точность",
            command=self.controller.change_precision,
            bg=button_default, fg=frame_fg, cursor=self.config.get("ui", "cursors", "button")
        )
        btn.grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.decorator_option_widgets.append(btn)

        # Панель выбора звуков
        sound_frame = tk.LabelFrame(self.options_panel, text="Звуки", fg=frame_fg, bg=frame_bg)
        sound_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)

        # Включение/выключение звуков
        chk = tk.Checkbutton(
            sound_frame, text="Звуки включены",
            variable=self.sound_options_vars["Звуки включены"],
            command=self.update_sound_functionality,
            bg=frame_bg, fg=frame_fg, selectcolor=selectcolor,
            activebackground=activebackground, cursor=self.config.get("ui", "cursors", "checkbox")
        )
        chk.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.sound_option_widgets.append(chk)

        # Выбор типа звука
        tk.Label(sound_frame, text="Тип звука:", bg=frame_bg, fg=frame_fg).grid(row=1, column=0, sticky="w", padx=5,
                                                                                pady=(10, 2))

        drums_radio = tk.Radiobutton(
            sound_frame, text="Барабаны",
            variable=self.sound_options_vars["Тип звука"],
            value="drums",
            command=self.update_sound_type,
            bg=frame_bg, fg=frame_fg, selectcolor=selectcolor,
            activebackground=activebackground, cursor=self.config.get("ui", "cursors", "button")
        )
        drums_radio.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.sound_option_widgets.append(drums_radio)

        memes_radio = tk.Radiobutton(
            sound_frame, text="Мемы",
            variable=self.sound_options_vars["Тип звука"],
            value="memes",
            command=self.update_sound_type,
            bg=frame_bg, fg=frame_fg, selectcolor=selectcolor,
            activebackground=activebackground, cursor=self.config.get("ui", "cursors", "button")
        )
        memes_radio.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.sound_option_widgets.append(memes_radio)

        # Настраиваем авторасширение
        self.options_panel.grid_columnconfigure(0, weight=1)
        self.options_panel.grid_columnconfigure(1, weight=1)
        self.options_panel.grid_columnconfigure(2, weight=1)
        self.options_panel.grid_columnconfigure(3, weight=1)

    def toggle_options_panel(self):
        """Показывает или скрывает панель опций"""
        if self.show_options_panel.get():
            self.options_panel.grid()
        else:
            self.options_panel.grid_remove()

    def update_functionality(self):
        """Обновляет калькулятор при изменении настроек"""
        selected_history_options = {key: var.get() for key, var in self.history_options_vars.items()}
        selected_options = {key: var.get() for key, var in self.options_vars.items()}

        if hasattr(self, 'decorator_options_vars'):
            selected_decorator_options = {key: var.get() for key, var in self.decorator_options_vars.items()}
            selected_sound_options = {key: var.get() for key, var in self.sound_options_vars.items()}
            self.controller.update_options(selected_options, selected_history_options, selected_decorator_options,
                                           selected_sound_options)
        else:
            self.controller.update_options(selected_options, selected_history_options)

    def update_decorator_functionality(self):
        """Обновляет настройки декораторов"""
        if hasattr(self, 'decorator_options_vars'):
            selected_history_options = {key: var.get() for key, var in self.history_options_vars.items()}
            selected_options = {key: var.get() for key, var in self.options_vars.items()}
            selected_decorator_options = {key: var.get() for key, var in self.decorator_options_vars.items()}
            selected_sound_options = {key: var.get() for key, var in self.sound_options_vars.items()}
            self.controller.update_options(selected_options, selected_history_options, selected_decorator_options,
                                           selected_sound_options)

    def update_sound_functionality(self):
        """Обновляет настройки звуков"""
        selected_sound_options = {key: var.get() for key, var in self.sound_options_vars.items()}
        self.sound_options = selected_sound_options

        # Обновляем контроллер
        selected_history_options = {key: var.get() for key, var in self.history_options_vars.items()}
        selected_options = {key: var.get() for key, var in self.options_vars.items()}
        selected_decorator_options = {key: var.get() for key, var in self.decorator_options_vars.items()}
        self.controller.update_options(selected_options, selected_history_options, selected_decorator_options,
                                       selected_sound_options)

    def update_sound_type(self):
        """Обновляет тип звуков"""
        sound_type = self.sound_options_vars["Тип звука"].get()
        self.selected_sounds = self.drums_sounds if sound_type == "drums" else self.mem_sounds
        self.update_sound_functionality()

    def update_buttons(self, options, buttons):
        """Динамически обновляет кнопки"""
        for widget in self.root.winfo_children():
            if isinstance(widget,
                          tk.Button) and widget not in self.decorator_option_widgets and widget not in self.history_option_widgets:
                widget.destroy()

        self.all_buttons = []

        row_val = self.config.get("grid_layout", "buttons_start_row")
        col_val = 0

        self.update_layout(len(buttons[0]))

        button_width = self.config.get("ui", "layout", "button_width") // self.config.get("ui", "layout",
                                                                                          "button_width_divisor")
        button_height = self.config.get("ui", "layout", "button_height") // self.config.get("ui", "layout",
                                                                                            "button_height_divisor")
        button_font_family = self.config.get("ui", "fonts", "button_font", "family")
        button_font_weight = self.config.get("ui", "fonts", "button_font", "weight")
        padding = self.config.get("ui", "layout", "padding")

        for row in buttons:
            for button in row:
                # Определяем цвет кнопки
                if button.isdigit():
                    fg_color = self.config.get("ui", "colors", "text_default")
                elif button == "=":
                    fg_color = self.config.get("ui", "colors", "text_default")
                elif button == "C":
                    fg_color = self.config.get("ui", "colors", "text_clear")
                elif button in ["MS", "MR", "M+", "MC"]:
                    fg_color = self.config.get("ui", "colors", "text_memory")
                else:
                    fg_color = self.config.get("ui", "colors", "text_operation")

                if button == "=":
                    bg_color = self.config.get("ui", "colors", "button_equals")
                else:
                    bg_color = self.config.get("ui", "colors", "button_default")

                btn = tk.Button(
                    self.root, text=button, width=button_width, height=button_height,
                    font=(button_font_family, self.base_font_size, button_font_weight),
                    fg=fg_color, bg=bg_color, cursor=self.config.get("ui", "cursors", "button"),
                    command=lambda b=button: [self.play_button_sound(), self.controller.on_button_click(b)]
                )
                btn.grid(row=row_val, column=col_val, sticky="nsew", padx=padding, pady=padding)
                self.all_buttons.append(btn)

                col_val += 1
            col_val = 0
            row_val += 1

        self.update_font_sizes()

    def update_decorator_options(self, decorator_options):
        """Обновляет опции декораторов"""
        self.decorator_options = decorator_options

        # Обновляем переключатели декораторов
        for key, val in decorator_options.items():
            if key in self.decorator_options_vars:
                self.decorator_options_vars[key].set(val)
            else:
                self.decorator_options_vars[key] = tk.BooleanVar(value=val)
                # Добавляем новый элемент в меню декораторов
                self.decorator_menu.add_checkbutton(
                    label=key,
                    variable=self.decorator_options_vars[key],
                    command=self.update_decorator_functionality
                )

    def update_sound_options(self, sound_options):
        """Обновляет опции звуков"""
        self.sound_options = sound_options

        # Обновляем переменные
        for key, val in sound_options.items():
            if key in self.sound_options_vars:
                self.sound_options_vars[key].set(val)

        # Обновляем выбранные звуки
        sound_type = sound_options.get("Тип звука", self.config.get("sounds", "default_options", "type"))
        self.selected_sounds = self.drums_sounds if sound_type == "drums" else self.mem_sounds

    def create_widgets(self):
        """Создает все элементы интерфейса"""

        # Поле ввода с горизонтальной полосой прокрутки
        self.entry_frame = tk.Frame(self.root, bg=self.config.get("ui", "colors", "background"))
        self.entry_frame.grid(row=self.config.get("grid_layout", "entry_row"), column=0, columnspan=10, sticky="nsew")

        entry_font_family = self.config.get("ui", "fonts", "entry_font", "family")
        entry_bg = self.config.get("ui", "colors", "entry_background")
        entry_fg = self.config.get("ui", "colors", "entry_foreground")
        entry_cursor = self.config.get("ui", "colors", "entry_cursor")

        self.entry = tk.Text(self.entry_frame, font=(entry_font_family, self.entry_font_size), bd=2, height=1,
                             bg=entry_bg, fg=entry_fg, insertbackground=entry_cursor, wrap="none", undo=True)
        self.entry.grid(row=1, column=0, sticky="ew")

        history_img_path = self.config.get("images", "history_button", "path")
        history_img_size = self.config.get("images", "history_button", "size")
        img_pil = Image.open(history_img_path)
        img_pil = img_pil.resize(tuple(history_img_size))
        self.img = ImageTk.PhotoImage(img_pil)

        tk.Button(
            self.entry_frame, image=self.img, compound="center",
            bg=self.config.get("ui", "colors", "button_default"), cursor=self.config.get("ui", "cursors", "button"),
            command=lambda: self.controller.show_history()
        ).grid(row=1, column=1, sticky="ew", padx=self.config.get("ui", "layout", "padding"),
               pady=self.config.get("ui", "layout", "padding"))

        style = ttk.Style()
        style.theme_use("clam")
        scrollbar_config = self.config.get("ui", "colors", "scrollbar")
        style.configure("Custom.Horizontal.TScrollbar",
                        troughcolor=scrollbar_config["troughcolor"],
                        background=scrollbar_config["background"],
                        bordercolor=scrollbar_config["bordercolor"],
                        arrowcolor=scrollbar_config["arrowcolor"])
        style.map("Custom.Horizontal.TScrollbar",
                  background=[("active", scrollbar_config["background"])])

        self.scrollbar = ttk.Scrollbar(self.entry_frame, orient="horizontal",
                                       command=self.entry.xview, cursor=self.config.get("ui", "cursors", "scrollbar"),
                                       style="Custom.Horizontal.TScrollbar")
        self.scrollbar.grid(row=2, column=0, columnspan=10, sticky="nsew")
        self.entry.config(xscrollcommand=self.scrollbar.set)

        # Привязка клавиш
        self.entry.bind("<KeyPress>", self.controller.on_key_press)

    def setup_layout(self):
        self.entry_frame.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.entry_frame.grid_rowconfigure(i, weight=1)

        for i in range(8):
            self.root.grid_rowconfigure(i, weight=5)

    def update_layout(self, len):
        """Обновляет выравнивание кнопок"""
        for i in range(len):
            self.root.grid_columnconfigure(i, weight=1)

    def get_entry_text(self):
        return self.entry.get("1.0", tk.END).strip()

    def clear_entry(self):
        self.entry.delete("1.0", tk.END)

    def set_entry_text(self, text):
        self.entry.delete("1.0", tk.END)
        self.entry.insert(tk.END, text)

    def insert_text(self, text):
        self.entry.insert(tk.END, text)

    def show_execution_time(self, time_ms):
        """Показывает время выполнения в статусной строке"""
        message_template = self.config.get("status_bar", "messages", "execution_time")
        self.status_bar.config(text=message_template.format(time=time_ms))

    def show_memory_status(self, status):
        """Показывает статус операций с памятью"""
        message_template = self.config.get("status_bar", "messages", "memory_operation")
        self.status_bar.config(text=message_template.format(operation=status))

    def show_status_message(self, message):
        """Показывает сообщение в статусной строке"""
        self.status_bar.config(text=message)

    def show_history_window(self, history):
        """Показывает окно истории"""
        history_window = tk.Toplevel(self.root)
        history_window.title(self.config.get("history", "window", "title"))

        window_width = self.config.get("history", "window", "width")
        window_height = self.config.get("history", "window", "height")
        history_window.geometry(f"{window_width}x{window_height}")

        history_frame = tk.Frame(history_window)
        history_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(history_frame)
        scrollbar = tk.Scrollbar(history_frame, orient="vertical",
                                 cursor=self.config.get("ui", "cursors", "scrollbar"), command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        history_font_family = self.config.get("history", "display", "font", "family")
        history_font_size = self.config.get("history", "display", "font", "size")
        label_width = self.config.get("history", "display", "label_width")
        row_padding = self.config.get("history", "display", "padding", "row")
        side_padding = self.config.get("history", "display", "padding", "side")

        for line in history:
            row_frame = tk.Frame(content_frame)
            row_frame.pack(fill="x", pady=row_padding)
            expr_label = tk.Label(row_frame, text=line, font=(history_font_family, history_font_size),
                                  width=label_width, anchor="w")
            expr_label.pack(side="left", padx=side_padding)
            insert_button = tk.Button(
                row_frame, text="Вставить", cursor=self.config.get("ui", "cursors", "button"),
                command=lambda expr=line: self.controller.insert_from_history(expr)
            )
            insert_button.pack(side="right", padx=side_padding)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        scale_factor = self.config.get("history", "window", "scale_factor")
        history_window.geometry(f"{int(self.root.winfo_width() * scale_factor)}x{self.root.winfo_height()}")
