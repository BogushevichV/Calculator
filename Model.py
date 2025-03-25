import math
import re


class CalculatorModel:
    """Модель калькулятора - отвечает за хранение данных и бизнес-логику"""

    def __init__(self):
        self.history_file = "calculator_history.txt"

    def calculate(self, expression):
        try:
            # Обрабатываем тригонометрические функции, квадратный корень и заменяем ^ на **
            expression = self.evaluate_trigonometric_functions(expression)
            expression = expression.replace("^", "**")
            expression = re.sub(r'√(\d+|\(.*?\))', r'math.sqrt(\1)', expression)

            # Вычисляем выражение
            result = eval(expression)

            # Ограничиваем точность результата
            return round(result, 5)
        except Exception:
            raise ValueError("Ошибка вычисления")

    @staticmethod
    def evaluate_trigonometric_functions(expression):
        expression = re.sub(r'sin\((.*?)\)', lambda m: str(math.sin(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cos\((.*?)\)', lambda m: str(math.cos(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'tan\((.*?)\)', lambda m: str(math.tan(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cot\((.*?)\)', lambda m: str(1 / math.tan(math.radians(float(m.group(1))))), expression)
        return expression

    def save_to_history(self, expression):
        try:
            with open(self.history_file, "r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        if len(lines) >= 100:
            lines.pop(0)

        lines.append(expression + "\n")

        with open(self.history_file, "w", encoding='utf-8') as file:
            file.writelines(lines)

    def get_history(self):
        try:
            with open(self.history_file, "r", encoding='utf-8') as file:
                return file.readlines()
        except FileNotFoundError:
            return ["История пуста"]
