#Controller.py
from Model import CalculatorModel
from View import CalculatorView
from Builder import CalculatorBuilder
from tkinter import filedialog, simpledialog

class CalculatorController:
    """Контроллер калькулятора - связывает модель и представление"""

    def __init__(self, root):
        self.builder = CalculatorBuilder()
        self.options, self.history_options, self.buttons = self.builder.build()

        self.model = CalculatorModel(self.options, self.history_options)
        self.view = CalculatorView(root, self, self.history_options, self.options, self.buttons)

    def update_options(self, selected_options, selected_history_options):
        """Обновляет функционал через Builder"""
        self.builder = CalculatorBuilder()  # Новый Строитель

        if selected_options["Научные функции"]:
            self.builder.add_scientific_functions()
        if selected_options["Программные операции"]:
            self.builder.add_programming_operations()
        if selected_options["Инженерные операции"]:
            self.builder.add_engineering_operations()

        self.builder.toggle_history_saving(selected_history_options["Сохранение выражений"])

        self.options, self.history_options, self.buttons = self.builder.build()
        self.model.update_options(self.options)
        self.model.update_history_options(self.history_options)
        self.view.update_buttons(self.options, self.buttons)

    def on_button_click(self, char):
        if char == "C":
            self.view.clear_entry()
        elif char == "=":
            try:
                expression = self.view.get_entry_text()
                result = self.model.calculate(expression)
                self.model.save_to_history(expression)
                self.view.set_entry_text(str(result))
            except Exception as ex:
                print(ex)
                self.view.set_entry_text("Ошибка")
        elif char in ["sin", "cos", "tan", "cot"]:
            self.view.insert_text(f"{char}(")
        elif char == "^":
            self.view.insert_text("^")
        else:
            self.view.insert_text(char)

    def show_history(self):
        history = self.model.get_history()
        self.view.show_history_window(history)

    def change_history_limit(self):
        """Изменяет лимит истории"""
        new_limit = simpledialog.askinteger("Лимит истории", 
                                          "Введите новый лимит истории:",
                                          initialvalue=self.history_options["Лимит истории"],
                                          minvalue=1, maxvalue=1000)
        if new_limit:
            self.history_options["Лимит истории"] = new_limit
            self.model.update_history_options(self.history_options)

    def change_history_path(self):
        """Изменяет путь к файлу истории"""
        new_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=self.history_options["Путь файла"],
            title="Выберите новый путь истории",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if new_path:
            self.history_options["Путь файла"] = new_path
            self.model.update_history_options(self.history_options)

    def insert_from_history(self, expression):
        self.view.set_entry_text(expression.strip())

    @staticmethod
    def on_key_press(event):
        """Обрабатывает нажатие клавиш"""
        allowed_keys = "0123456789+-*/.=acdegilmnoprstx()^√"

        if event.char not in allowed_keys and event.keysym not in ["BackSpace", "Return", "Tab", "Left", "Right"]:
            return "break"