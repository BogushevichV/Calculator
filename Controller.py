from Model import CalculatorModel
from View import CalculatorView


class CalculatorController:
    """Контроллер калькулятора - связывает модель и представление"""

    def __init__(self, root):
        self.model = CalculatorModel()
        self.view = CalculatorView(root, self)

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
        allowed_keys = "0123456789+-*/.=sinco()^√"
        if event.char not in allowed_keys and event.keysym not in ["BackSpace", "Return", "Tab", "Left", "Right"]:
            return "break"