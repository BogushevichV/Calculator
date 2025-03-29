import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk

class CalculatorView:
    """Представление калькулятора - отвечает за отображение интерфейса"""

    def __init__(self, root, controller, options, buttons):
        self.buttons = None
        self.scrollbar = None
        self.img = None
        self.entry = None
        self.entry_frame = None
        self.root = root
        self.controller = controller

        self.options = options
        self.buttons = buttons

        self.root.title("Калькулятор")
        self.root.geometry("500x500")
        self.root.configure(bg="#212224")

        self.create_option_menu()
        self.create_widgets()
        self.update_buttons(self.options, self.buttons)
        self.setup_layout()

    def create_option_menu(self):
        """Создает меню выбора функционала"""
        self.options_frame = tk.Frame(self.root, bg="#212224")
        self.options_frame.grid(row=0, column=0, columnspan=10, sticky="nsew")

        self.options_vars = {
            key: tk.BooleanVar(value=val) for key, val in self.options.items()
        }

        col = 0
        for option in self.options_vars:
            chk = tk.Checkbutton(
                self.options_frame, text=option, variable=self.options_vars[option],
                command=self.update_functionality
            )
            chk.grid(row=0, column=col, sticky="nsew")
            col += 1

    def update_functionality(self):
        """Обновляет калькулятор при изменении настроек"""
        selected_options = {key: var.get() for key, var in self.options_vars.items()}
        self.controller.update_options(selected_options)

    def update_buttons(self, options, buttons):
        """Динамически обновляет кнопки"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        row_val = 3
        col_val = 0

        self.update_layout(len(buttons[0]))

        for row in buttons:
            for button in row:
                btn = tk.Button(
                    self.root, text=button, width=60 // 10, height=60 // 30, font=("Arial", 15, "bold"),
                    fg="white" if button.isdigit() or button == "=" else ("#038575" if button == "C" else "#327eed"),
                    bg="#307af7" if button == "=" else "#24282c",
                    command=lambda b=button: self.controller.on_button_click(b)
                )
                btn.grid(row=row_val, column=col_val, sticky="nsew", padx=1, pady=1)

                col_val += 1
            col_val = 0
            row_val += 1

    def create_widgets(self):
        """Создает все элементы интерфейса"""

        # Поле ввода с горизонтальной полосой прокрутки
        self.entry_frame = tk.Frame(self.root, bg="#212224")
        self.entry_frame.grid(row=1, column=0, columnspan=10, sticky="nsew")

        self.entry = tk.Text(self.entry_frame, font=("Arial", 25), bd=2, height=1,
                             bg="black", fg="white", insertbackground="white", wrap="none", undo=True)
        self.entry.grid(row=1, column=0, sticky="ew")

        # Кнопка истории
        img_pil = Image.open("img/history.png")
        img_pil = img_pil.resize((50, 50))
        self.img = ImageTk.PhotoImage(img_pil)

        tk.Button(
            self.entry_frame, image=self.img, compound="center",
            bg="#26292e",
            command=lambda: self.controller.show_history()
        ).grid(row=1, column=1, sticky="ew", padx=1, pady=1)

        # Настройка скроллбара
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
                                       command=self.entry.xview,
                                       style="Custom.Horizontal.TScrollbar")
        self.scrollbar.grid(row=2, column=0, columnspan=10, sticky="nsew")
        self.entry.config(xscrollcommand=self.scrollbar.set)

        # Привязка клавиш
        self.entry.bind("<KeyPress>", self.controller.on_key_press)

    def setup_layout(self):
        """Настраивает расположение элементов"""
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
        """Возвращает текст из поля ввода"""
        return self.entry.get("1.0", tk.END).strip()

    def clear_entry(self):
        """Очищает поле ввода"""
        self.entry.delete("1.0", tk.END)

    def set_entry_text(self, text):
        """Устанавливает текст в поле ввода"""
        self.entry.delete("1.0", tk.END)
        self.entry.insert(tk.END, text)

    def insert_text(self, text):
        """Вставляет текст в текущую позицию курсора"""
        self.entry.insert(tk.END, text)

    def show_history_window(self, history):
        """Отображает окно истории"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История")
        history_window.geometry("450x500")

        history_frame = tk.Frame(history_window)
        history_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(history_frame)
        scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=canvas.yview)
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
                row_frame, text="Вставить",
                command=lambda expr=line: self.controller.insert_from_history(expr)
            )
            insert_button.pack(side="right", padx=5)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        history_window.geometry(f"{int(self.root.winfo_width() * 0.9)}x{self.root.winfo_height()}")
