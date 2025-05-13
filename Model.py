# Model.py
import math
import re
from Decorator import ICalculator

class CalculatorModel(ICalculator):
    """Модель калькулятора - отвечает за хранение данных и бизнес-логику"""

    def __init__(self, options, history_options):
        self.history_options = history_options
        self.options = options

    def calculate(self, expression):
        try:
            # Обрабатываем тригонометрические функции, квадратный корень и заменяем ^ на **
            expression = self.preprocess_expression(expression)

            # Вычисляем выражение
            result = eval(expression)

            # Ограничиваем точность результата (базовая точность)
            return result
        except Exception:
            raise ValueError("Ошибка вычисления")

    @staticmethod
    def preprocess_expression(expression):
        """Обрабатывает специальные функции перед вычислением"""
        expression = expression.replace("^", "**")  # Замена ^ на **

        """Обрабатывает тригонометрические функции в выражении"""
        expression = re.sub(r'sin\((.*?)\)', lambda m: str(math.sin(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cos\((.*?)\)', lambda m: str(math.cos(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'tan\((.*?)\)', lambda m: str(math.tan(math.radians(float(m.group(1))))), expression)
        expression = re.sub(r'cot\((.*?)\)', lambda m: str(1 / math.tan(math.radians(float(m.group(1))))), expression)

        # Корень √(число)
        expression = re.sub(r'√(\d+|\(.*?\))', r'math.sqrt(\1)', expression)

        # Логарифмы log(число), exp(число)
        expression = re.sub(r'log(\d+|\(.*?\))', lambda m: str(math.log(float(m.group(1)))), expression)
        expression = re.sub(r'exp(\d+|\(.*?\))', lambda m: str(math.exp(float(m.group(1)))), expression)

        # Остаток от деления mod (a mod b -> a % b)
        expression = re.sub(r'(\d+)\s*mod\s*(\d+)', r'(\1 % \2)', expression)

        # Побитовые операции (AND, OR, XOR, NOT)
        expression = re.sub(r'(\d+)\s*and\s*(\d+)', lambda m: str(int(m.group(1)) & int(m.group(2))), expression)
        expression = re.sub(r'(\d+)\s*or\s*(\d+)', lambda m: str(int(m.group(1)) | int(m.group(2))), expression)
        expression = re.sub(r'(\d+)\s*xor\s*(\d+)', lambda m: str(int(m.group(1)) ^ int(m.group(2))), expression)
        expression = re.sub(r'not(\d+|\(.*?\))', lambda m: str(255 - eval(m.group(1))), expression)

        return expression

    def update_options(self, options):
        """Обновляет список доступных операций"""
        self.options = options

    def update_history_options(self, history_options):
        """Обновляет настройки истории"""
        self.history_options = history_options

    def save_to_history(self, expression):
        """Сохраняет выражение в истории"""
        if not self.history_options.get("Сохранение выражений", True):
            return  # Не сохраняем, если опция отключена
        
        try:
            # Читаем существующую историю
            with open(self.history_options["Путь файла"], "r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        # Удаляем первую запись, если лимит превышен
        if len(lines) >= self.history_options["Лимит истории"]:
            lines.pop(0)

        lines.append(expression + "\n")

        # Записываем историю обратно в файл
        with open(self.history_options["Путь файла"], "w", encoding='utf-8') as file:
            file.writelines(lines)

    def get_history(self):
        try:
            with open(self.history_options["Путь файла"], "r", encoding='utf-8') as file:
                return file.readlines()
        except FileNotFoundError:
            return ["История пуста"]