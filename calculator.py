import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import math
import re


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("500x500")
        self.root.configure(bg="#212224")
        self.create_widgets()

    def create_widgets(self):
        # Поле ввода с горизонтальной полосой прокрутки
        self.entry_frame = tk.Frame(self.root, bg="#212224")
        self.entry_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")

        self.entry = tk.Text(self.entry_frame, font=("Arial", 25), bd=2, height=1,
                             bg="black", fg="white", insertbackground="white", wrap="none", undo=True)
        self.entry.grid(row=1, column=0, sticky="ew")

        img_pil = Image.open("img/history.png")
        img_pil = img_pil.resize((50, 50))
        self.img = ImageTk.PhotoImage(img_pil)

        tk.Button(
            self.entry_frame, image=self.img, compound="center",
                bg="#26292e",
            command=lambda b="История": self.on_button_click(b)
        ).grid(row=1, column=1, sticky="ew", padx=1, pady=1)

        self.entry_frame.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.entry_frame.grid_rowconfigure(i, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Custom.Horizontal.TScrollbar",
                        troughcolor="black",
                        background="#636363",
                        bordercolor="black",
                        arrowcolor="black")

        style.map("Custom.Horizontal.TScrollbar",
                  background=[("active", "#636363")])  # Цвет при наведении

        self.scrollbar = ttk.Scrollbar(self.entry_frame, orient="horizontal",
                                       command=self.entry.xview,
                                       style="Custom.Horizontal.TScrollbar")

        self.scrollbar.grid(row=2, column=0, columnspan=5, sticky="nsew")
        self.entry.config(xscrollcommand=self.scrollbar.set)

        buttons = [
            '7', '8', '9', '/', 'sin',
            '4', '5', '6', '*', 'cos',
            '1', '2', '3', '-', 'tan',
            'C', '0', '.', '+', 'cot',
            '=', '(', ')', '√', '^'
        ]

        row_val = 2
        col_val = 0
        button_size = 60

        for button in buttons:
            tk.Button(
                self.root, text=button, width=button_size // 10, height=button_size // 30, font=("Arial", 15, "bold"),
                fg="white" if button.isdigit() or button == "=" else ("#038575" if button == "C" else "#327eed"),
                bg="#307af7" if button=="=" else "#24282c",
                command=lambda b=button: self.on_button_click(b)
            ).grid(row=row_val, column=col_val, sticky="nsew", padx=1, pady=1)
            col_val += 1
            if col_val > 4:
                col_val = 0
                row_val += 1

        for i in range(8):
            self.root.grid_rowconfigure(i, weight=5)

        for i in range(5):
            self.root.grid_columnconfigure(i, weight=1)

        self.entry.bind("<KeyPress>", self.on_key_press)

    def on_button_click(self, char):
        current_text = self.entry.get("1.0", tk.END).strip()

        if char == "C":
            self.entry.delete("1.0", tk.END)
        elif char == "=":
            try:
                # Получаем введенное выражение
                expression = self.entry.get("1.0", tk.END).strip()

                text = expression.replace("√(", "sqrt(")

                # Сохраняем выражение в файл
                self.save_to_file(text)

                # Обрабатываем тригонометрические функции, квадратный корень и заменяем ^ на **
                expression = self.evaluate_trigonometric_functions(expression)
                expression = expression.replace("^", "**")
                expression = expression.replace("√(", "math.sqrt(")

                # Вычисляем выражение
                result = eval(expression)

                # Ограничиваем точность результата
                result = round(result, 5)

                # Отображаем результат
                self.entry.delete("1.0", tk.END)
                self.entry.insert(tk.END, str(result))
            except Exception as ex:
                print(ex)
                self.entry.delete("1.0", tk.END)
                self.entry.insert(tk.END, "Ошибка")
        elif char in ["sin", "cos", "tan", "cot", "√"]:
            self.entry.insert(tk.END, f"{char}(")
        elif char == "История":
            self.show_history()
        elif char == "^":
            self.entry.insert(tk.END, "^")  # Вставляем символ степени
        else:
            self.entry.insert(tk.END, char)

    def evaluate_trigonometric_functions(self, expression):
        expression = re.sub(r'sin\((.*?)\)', lambda m: str(math.sin(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cos\((.*?)\)', lambda m: str(math.cos(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'tan\((.*?)\)', lambda m: str(math.tan(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cot\((.*?)\)', lambda m: str(1 / math.tan(math.radians(float(m.group(1))))), expression)
        return expression

    def save_to_file(self, expression):
        try:
            # Читаем существующую историю
            with open("calculator_history.txt", "r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []  # Если файл не найден, начинаем с пустой истории

        # Удаляем первую запись, если лимит превышен
        if len(lines) >= 100:
            lines.pop(0)

        # Добавляем новую запись
        lines.append(expression + "\n")

        # Записываем историю обратно в файл
        with open("calculator_history.txt", "w") as file:
            file.writelines(lines)

    def show_history(self):
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

        try:
            with open("calculator_history.txt", "r") as file:
                history = file.readlines()
        except FileNotFoundError:
            history = ["История пуста"]

        for line in history:
            expression = line.strip().replace("sqrt(", "√(")
            row_frame = tk.Frame(content_frame)
            row_frame.pack(fill="x", pady=2)
            expr_label = tk.Label(row_frame, text=expression, font=("Arial", 12), width=30, anchor="w")
            expr_label.pack(side="left", padx=5)
            insert_button = tk.Button(row_frame, text="Вставить", command=lambda expr=expression: self.insert_expression(expr))
            insert_button.pack(side="right", padx=5)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        history_window.geometry(f"{int(self.root.winfo_width() * 0.9)}x{self.root.winfo_height()}")

    def insert_expression(self, expression):
        self.entry.delete("1.0", tk.END)
        self.entry.insert(tk.END, expression)

    def on_key_press(self, event):
        allowed_keys = "0123456789+-*/.=sinco()^√"
        if event.char not in allowed_keys and event.keysym not in ["BackSpace", "Return", "Tab", "Left", "Right"]:
            return "break"


if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()
