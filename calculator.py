import tkinter as tk
import math
import re


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("500x500")
        # Кот.
        root.iconbitmap("res/cat.ico")
        self.create_widgets()

    def create_widgets(self):
        # Поле ввода с горизонтальной полосой прокрутки
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.grid(row=0, column=0, columnspan=5, sticky="ew")

        self.entry = tk.Text(self.entry_frame, font=("Arial", 20), bd=2, height=1, width=32, wrap="none", undo=True)
        self.entry.grid(row=0, column=0, sticky="ew")

        self.scrollbar = tk.Scrollbar(self.entry_frame, orient="horizontal", command=self.entry.xview)
        self.scrollbar.grid(row=1, column=0, sticky="ew")
        self.entry.config(xscrollcommand=self.scrollbar.set)

        operation_buttons = [
            '+', '-', '*', '/', '^',
            'sin', 'cos', 'tan', 'cot', '√'
        ]

        numpad_buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            'C', '0', '.',
        ]

        row_val = 1
        col_val = 0
        button_size = 60

        for button in operation_buttons:
            tk.Button(
                self.root, text=button, width=button_size // 10, height=button_size // 30, font=("Arial", 15),
                command=lambda b=button: self.on_button_click(b)
            ).grid(row=row_val, column=col_val, sticky="nsew", padx=1, pady=1)
            col_val += 1
            if col_val >= 5:
                col_val = 0
                row_val += 1
        
        row_val = 3
        col_val = 0

        for button in numpad_buttons:
            tk.Button(
                self.root, text=button, width=button_size // 10, height=button_size // 30, font=("Arial", 15),
                command=lambda b=button: self.on_button_click(b)
            ).grid(row=row_val, column=col_val, sticky="nsew", padx=1, pady=1)
            col_val += 1
            if col_val >= 3:
                col_val = 0
                row_val += 1

        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(5):
            self.root.grid_columnconfigure(i, weight=1)

        tk.Button(
            self.root, text='(', width=button_size // 10, height=button_size // 30, font=("Arial", 15),
            command=lambda b='(': self.on_button_click(b)
        ).grid(row=3, column=3, sticky="nsew", padx=1, pady=1)
        tk.Button(
            self.root, text=')', width=button_size // 10, height=button_size // 30, font=("Arial", 15),
            command=lambda b=')': self.on_button_click(b)
        ).grid(row=3, column=4, sticky="nsew", padx=1, pady=1)
        tk.Button(
            self.root, text='История', width=button_size // 10, height=button_size // 30, font=("Arial", 15),
            command=lambda b='История': self.on_button_click(b)
        ).grid(row=6, column=3, sticky="nsew", padx=1, pady=1)
        tk.Button(
            self.root, text='=', width=button_size // 10, height=button_size // 30, font=("Arial", 15),
            command=lambda b='=': self.on_button_click(b)
        ).grid(row=6, column=4, sticky="nsew", padx=1, pady=1)

        self.entry.bind("<KeyPress>", self.on_key_press)

    def on_button_click(self, char):
        if char == "C":
            self.entry.delete("1.0", tk.END)
        elif char == "=":
            try:
                # Получаем введенное выражение
                expression = self.entry.get("1.0", tk.END).strip()

                # Сохраняем выражение в файл
                self.save_to_file(expression)

                # Обрабатываем тригонометрические функции, квадратный корень и заменяем ^ на **
                expression = self.evaluate_trigonometric_functions(expression)
                expression = expression.replace("^", "**")
                # Заменяет корни на программные.
                expression = re.sub(r'√(\d+|\(.*?\))', r'math.sqrt(\1)', expression)

                # Вычисляем выражение
                result = eval(expression)

                # Ограничиваем точность результата
                result = round(result, 5)

                # Отображаем результат
                self.entry.delete("1.0", tk.END)
                self.entry.insert(tk.END, str(result))
            except Exception as err:
                self.entry.delete("1.0", tk.END)
                print(err)
                self.entry.insert(tk.END, "Ошибка")
        elif char in ["sin", "cos", "tan", "cot"]:
            self.entry.insert(tk.END, f"{char}(")
        elif char == "История":
            self.show_history()
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
            with open("calculator_history.txt", "r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []  # Если файл не найден, начинаем с пустой истории

        # Удаляем первую запись, если лимит превышен
        if len(lines) >= 100:
            lines.pop(0)

        # Добавляем новую запись
        lines.append(expression + "\n")

        # Записываем историю обратно в файл
        with open("calculator_history.txt", "w", encoding="utf-8") as file:
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
            with open("calculator_history.txt", "r", encoding='utf-8') as file:
                history = file.readlines()
        except FileNotFoundError:
            history = ["История пуста"]

        for line in history:
            expression = line.strip()
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
