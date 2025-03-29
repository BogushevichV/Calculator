from Model import CalculatorModel
from View import CalculatorView
from Builder import CalculatorBuilder


class CalculatorController:
    """Контроллер калькулятора - связывает модель и представление"""

    def __init__(self, root):
        self.builder = CalculatorBuilder()
        self.options, self.buttons = self.builder.build()

        self.model = CalculatorModel(self.options)
        self.view = CalculatorView(root, self, self.options, self.buttons)

    def update_options(self, selected_options):
        """Обновляет функционал через Builder"""
        self.builder = CalculatorBuilder()  # Новый Строитель

        if selected_options["Научные функции"]:
            self.builder.add_scientific_functions()
        if selected_options["Программные операции"]:
            self.builder.add_programming_operations()
        if selected_options["Инженерные операции"]:
            self.builder.add_engineering_operations()

        self.options, self.buttons = self.builder.build()
        self.model.update_options(self.options)
        self.view.update_buttons(self.options, self.buttons)

    def on_button_click(self, char):
        """Обрабатывает нажатие кнопки"""
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
        """Показывает историю вычислений"""
        history = self.model.get_history()
        self.view.show_history_window(history)

    def insert_from_history(self, expression):
        """Вставляет выражение из истории в калькулятор"""
        self.view.set_entry_text(expression.strip())

    @staticmethod
    def on_key_press(event):
        """Обрабатывает нажатие клавиш"""
        allowed_keys = "0123456789+-*/.=acdegilmnoprstx()^√"
        if event.char not in allowed_keys and event.keysym not in ["BackSpace", "Return", "Tab", "Left", "Right"]:
            return "break"