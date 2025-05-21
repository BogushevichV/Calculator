import random
import winsound
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import math
import sys

class CalculatorView:
    """Представление калькулятора - отвечает за отображение интерфейса"""

    def __init__(self, root, controller, history_options, options, buttons, decorator_options=None):
        self.root = root

        self.buttons = None
        self.scrollbar = None
        self.img = None
        self.entry = None
        self.entry_frame = None

        self.controller = controller

        self.base_font_size = 15
        self.entry_font_size = 25
        self.options_font_size = 10

        self.initial_width = 525
        self.initial_height = 500

        self.scale_factor = 1

        self.history_options = history_options
        self.options = options
        self.buttons = buttons
        self.decorator_options = decorator_options or {}

        self.button_sounds = [
            "sounds/o-privet.wav",
            "sounds/shizofreniya.wav",
            "sounds/nani.wav",
            "sounds/aaaa-za-donbass.wav",
            "sounds/nea.wav",
            "sounds/vstavay.wav",
            "sounds/nyanpasu.wav",
            "sounds/sasha-tyi-yuvelir.wav",
            "sounds/ne-nado-diadia.wav",
            "sounds/diadia-sasha.wav"
        ]

        self.root.title("Калькулятор")
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")
        self.root.configure(bg="#212224")
        img = Image.open("img/icon.png")
        photo = ImageTk.PhotoImage(img)
        self.root.iconphoto(False, photo)
        self.root.bind("<Configure>", self.on_window_resize)

        try:
            # Загрузка изображения курсора
            cursor_img = Image.open("img/clown-face-cursor.png")
            cursor_img = cursor_img.resize((32, 32), Image.Resampling.LANCZOS)

            # Создание курсора (только для Windows)
            if sys.platform == 'win32':
                from ctypes import windll, create_string_buffer

                # Конвертируем изображение в формат .cur
                cursor_img.save("img/temp.cur", format="ICO")

                # Загружаем курсор
                h_cursor = windll.user32.LoadImageW(
                    0, "img/temp.cur", 2, 0, 0, 0x00000010
                )
                cursor = "@img/temp.cur"
                self.root.config(cursor=cursor)
            else:
                # Для других ОС используем стандартный курсор
                self.root.config(cursor="spraycan")

        except Exception as e:
            print(f"Ошибка загрузки курсора: {e}")
            self.root.config(cursor="spraycan")

        self.all_buttons = []
        self.history_option_widgets = []
        self.option_checkbuttons = []
        self.decorator_option_widgets = []

        # Создаем главное меню вместо отдельных опций
        self.create_menu_bar()
        
        self.create_widgets()
        self.update_buttons(self.options, self.buttons)
        self.setup_layout()
        
        # Создаем статусную строку для вывода информации о времени выполнения и т.д.
        self.status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=30)
        self.status_bar.grid(row=100, column=0, columnspan=10, sticky="nsew")

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
            self.scale_factor = max(0.7, min(self.scale_factor, 2.0))

            # Обновляем размер шрифта для всех элементов
            self.update_font_sizes()

    def play_button_sound(self):
        """Воспроизводит случайный звук при нажатии кнопки"""
        try:
            sound_file = random.choice(self.button_sounds)
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

    def update_font_sizes(self):
        """Обновляет размеры шрифтов для всех элементов интерфейса"""
        # Обновляем шрифт кнопок
        new_button_font = ("Arial", int(self.base_font_size * self.scale_factor), "bold")
        for button in self.all_buttons:
            button.config(font=new_button_font)

        # Обновляем шрифт поля ввода
        new_entry_font = ("Arial", int(self.entry_font_size * self.scale_factor))
        self.entry.config(font=new_entry_font)

        # Обновляем шрифт чекбоксов
        new_option_font = ("Arial", int(self.options_font_size * self.scale_factor))
        for chk in self.option_checkbuttons:
            chk.config(font=new_option_font)

        for widget in self.history_option_widgets:
            widget.config(font=new_option_font)
            
        for widget in self.decorator_option_widgets:
            widget.config(font=new_option_font)

    def create_menu_bar(self):
        """Создает верхнее меню для всех опций"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Создаем меню функций
        self.functions_menu = tk.Menu(self.menu_bar,tearoff=0,)
        self.menu_bar.add_cascade(label="Функции", menu=self.functions_menu)

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
        self.menu_bar.add_cascade(label="История", menu=self.history_menu)

        # Создаем переменные для хранения настроек истории
        self.history_options_vars = {
            "Сохранение выражений": tk.BooleanVar(value=self.history_options["Сохранение выражений"]),
            "Лимит истории": tk.IntVar(value=self.history_options["Лимит истории"]),
            "Путь файла": tk.StringVar(value=self.history_options["Путь файла"]),
        }

        # Добавляем элементы в меню истории
        self.history_menu.add_checkbutton(
            label="Сохранение выражений",
            variable=self.history_options_vars["Сохранение выражений"],
            command=self.update_functionality
        )
        self.history_menu.add_command(
            label="Изменить лимит истории",
            command=self.controller.change_history_limit
        )
        self.history_menu.add_command(
            label="Изменить путь файла истории",
            command=self.controller.change_history_path
        )
        self.history_menu.add_separator()
        self.history_menu.add_command(
            label="Показать историю",
            command=lambda: self.controller.show_history()
        )

        # Создаем меню декораторов
        self.decorator_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Декораторы", menu=self.decorator_menu)

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
            label="Изменить точность",
            command=self.controller.change_precision
        )

        # Добавляем меню "Вид" для управления интерфейсом
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Вид", menu=self.view_menu)

        # Добавляем переменную для переключения панели опций
        self.show_options_panel = tk.BooleanVar(value=False)
        self.view_menu.add_checkbutton(
            label="Показать панель опций",
            variable=self.show_options_panel,
            command=self.toggle_options_panel
        )

        # Создаем скрытую панель для опций
        self.create_options_panel()

    def create_options_panel(self):
        """Создает панель опций, которая будет скрыта/показана по запросу"""
        self.options_panel = tk.Frame(self.root, bg="#212224")
        self.options_panel.grid(row=1, column=0, columnspan=10, sticky="nsew")
        self.options_panel.grid_remove()  # Скрываем панель по умолчанию
        
        # Панель функций
        functions_frame = tk.LabelFrame(self.options_panel, text="Функции", fg="white", bg="#24282c")
        functions_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        row = 0
        for option, var in self.options_vars.items():
            chk = tk.Checkbutton(
                functions_frame, text=option, variable=var,
                command=self.update_functionality,cursor="pencil", bg="#24282c", fg="white",
                selectcolor="#212224", activebackground="#24282c"
            )
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            self.option_checkbuttons.append(chk)
            row += 1
        
        # Панель истории
        history_frame = tk.LabelFrame(self.options_panel, text="История", fg="white", bg="#24282c")
        history_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Сохранение выражений
        chk = tk.Checkbutton(
            history_frame, text="Сохранение выражений",
            variable=self.history_options_vars["Сохранение выражений"],
            command=self.update_functionality, bg="#24282c", fg="white",
            selectcolor="#212224", activebackground="#24282c", cursor="pencil"
        )
        chk.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(chk)
        
        # Лимит истории
        btn = tk.Button(
            history_frame, text="Изменить лимит истории",
            command=self.controller.change_history_limit,
            bg="#307af7", fg="white", cursor="hand2"
        )
        btn.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(btn)
        
        # Путь к файлу
        btn = tk.Button(
            history_frame, text="Изменить путь файла истории",
            command=self.controller.change_history_path,
            bg="#307af7", fg="white", cursor="hand2"
        )
        btn.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.history_option_widgets.append(btn)
        
        # Панель декораторов
        decorator_frame = tk.LabelFrame(self.options_panel, text="Декораторы", fg="white", bg="#24282c")
        decorator_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        row = 0
        for option, var in self.decorator_options_vars.items():
            chk = tk.Checkbutton(
                decorator_frame, text=option,
                variable=var,
                command=self.update_decorator_functionality,
                bg="#24282c", fg="white", selectcolor="#212224", activebackground="#24282c",cursor="pencil"
            )
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            self.decorator_option_widgets.append(chk)
            row += 1
        
        # Кнопка точности
        btn = tk.Button(
            decorator_frame, text="Изменить точность",
            command=self.controller.change_precision,
            bg="#307af7", fg="white", cursor="hand2"
        )
        btn.grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.decorator_option_widgets.append(btn)
        
        # Настраиваем авторасширение
        self.options_panel.grid_columnconfigure(0, weight=1)
        self.options_panel.grid_columnconfigure(1, weight=1)
        self.options_panel.grid_columnconfigure(2, weight=1)

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
            self.controller.update_options(selected_options, selected_history_options, selected_decorator_options)
        else:
            self.controller.update_options(selected_options, selected_history_options)
            
    def update_decorator_functionality(self):
        """Обновляет настройки декораторов"""
        if hasattr(self, 'decorator_options_vars'):
            selected_history_options = {key: var.get() for key, var in self.history_options_vars.items()}
            selected_options = {key: var.get() for key, var in self.options_vars.items()}
            selected_decorator_options = {key: var.get() for key, var in self.decorator_options_vars.items()}
            self.controller.update_options(selected_options, selected_history_options, selected_decorator_options)

    def update_buttons(self, options, buttons):
        """Динамически обновляет кнопки"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget not in self.decorator_option_widgets and widget not in self.history_option_widgets:
                widget.destroy()

        self.all_buttons = []

        row_val = 3  # Оставляем место для панели опций
        col_val = 0

        self.update_layout(len(buttons[0]))

        for row in buttons:
            for button in row:
                # Определяем цвет кнопки
                fg_color = "white" if button.isdigit() or button == "=" else ("#038575" if button == "C" else "#327eed")
                bg_color = "#307af7" if button == "=" else "#24282c"
                
                # Особый цвет для кнопок памяти
                if button in ["MS", "MR", "M+", "MC"]:
                    fg_color = "#ffcc00"
                
                btn = tk.Button(
                    self.root, text=button, width=60 // 10, height=60 // 30, font=("Arial", 15, "bold"),
                    fg=fg_color, bg=bg_color, cursor="hand2",
                    command=lambda b=button: [self.play_button_sound(), self.controller.on_button_click(b)]
                )
                btn.grid(row=row_val, column=col_val, sticky="nsew", padx=1, pady=1)
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

    def create_widgets(self):
        """Создает все элементы интерфейса"""

        # Поле ввода с горизонтальной полосой прокрутки
        self.entry_frame = tk.Frame(self.root, bg="#212224")
        self.entry_frame.grid(row=2, column=0, columnspan=10, sticky="nsew")

        self.entry = tk.Text(self.entry_frame, font=("Arial", 25), bd=2, height=1,
                             bg="black", fg="white", insertbackground="white", wrap="none", undo=True)
        self.entry.grid(row=1, column=0, sticky="ew")

        img_pil = Image.open("img/history.png")
        img_pil = img_pil.resize((50, 50))
        self.img = ImageTk.PhotoImage(img_pil)

        tk.Button(
            self.entry_frame, image=self.img, compound="center",
            bg="#26292e", cursor="hand2",
            command=lambda: self.controller.show_history()
        ).grid(row=1, column=1, sticky="ew", padx=1, pady=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TScrollbar",
                        troughcolor="black",
                        background="#636363",
                        bordercolor="black",
                        arrowcolor="black")
        style.map("Custom.Horizontal.TScrollbar",
                  background=[("active", "#636363")])

        self.scrollbar = ttk.Scrollbar(self.entry_frame, orient="horizontal",
                                       command=self.entry.xview, cursor="hand1",
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
        self.status_bar.config(text=f"Время выполнения: {time_ms:.3f} мс")
        
    def show_memory_status(self, status):
        """Показывает статус операций с памятью"""
        self.status_bar.config(text=status)
        
    def show_status_message(self, message):
        """Показывает сообщение в статусной строке"""
        self.status_bar.config(text=message)
    
    def show_history_window(self, history):
        """Показывает окно истории"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История")
        history_window.geometry("450x500")

        history_frame = tk.Frame(history_window)
        history_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(history_frame)
        scrollbar = tk.Scrollbar(history_frame, orient="vertical", cursor="hand1",command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        for line in history:
            row_frame = tk.Frame(content_frame)
            row_frame.pack(fill="x", pady=2)
            expr_label = tk.Label(row_frame, text=line, font=("Arial", 12), width=30, anchor="w")
            expr_label.pack(side="left", padx=5)
            insert_button = tk.Button(
                row_frame, text="Вставить",cursor="hand2",
                command=lambda expr=line: self.controller.insert_from_history(expr)
            )
            insert_button.pack(side="right", padx=5)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        history_window.geometry(f"{int(self.root.winfo_width() * 0.9)}x{self.root.winfo_height()}")