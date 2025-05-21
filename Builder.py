# Builder.py
import json


class CalculatorBuilder:
    """Строитель калькулятора, отвечает за поэтапное добавление функций"""

    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.options = {
            "Научные функции": config['calculator_options']['scientific_functions'],
            "Программные операции": config['calculator_options']['programming_operations'],
            "Инженерные операции": config['calculator_options']['engineering_operations']
        }

        self.buttons = config['button_layout']['basic']

        self.history_options = {
            "Сохранение выражений": config['history_options']['save_expressions'],
            "Лимит истории": config['history_options']['limit'],
            "Путь файла": config['history_options']['file_path']
        }

        self.decorator_options = {
            "Измерение времени": config['decorator_options']['timing'],
            "Память": config['decorator_options']['memory'],
            "Настраиваемая точность": config['decorator_options']['precision']
        }

        self.precision_value = config['decorator_options']['default_precision']

    def add_scientific_functions(self):
        """Добавляет научные функции"""
        self.options["Научные функции"] = True
        self.add_buttons(['sin', 'cos', 'tan', 'cot', '√', '^'])
        return self

    def add_programming_operations(self):
        """Добавляет программные операции"""
        self.options["Программные операции"] = True
        self.add_buttons(['and', 'or', 'xor', 'not'])
        return self

    def add_engineering_operations(self):
        """Добавляет инженерные операции"""
        self.options["Инженерные операции"] = True
        self.add_buttons(['log', 'exp', 'mod'])
        return self
    
    def toggle_history_saving(self, enabled=True):
        """Включает или выключает сохранение выражений в историю"""
        self.history_options["Сохранение выражений"] = enabled
        return self

    def set_history_limit(self, limit):
        """Устанавливает лимит истории"""
        self.history_options["Лимит истории"] = limit
        return self

    def set_history_file_path(self, file_path):
        """Устанавливает путь к файлу истории"""
        self.history_options["Путь файла"] = file_path
        return self

    def add_buttons(self, new_buttons):
        j = 0
        for i in range(5):
            if i >= len(new_buttons):
                break
            self.buttons[j].append(new_buttons[i])
            j += 1

        for button in new_buttons[5:]:
            self.buttons[
                min(range(len(self.buttons)), key=lambda i: len(self.buttons[i]))
            ].append(button)

    def add_timing_decorator(self):
        """Добавляет декоратор измерения времени"""
        self.decorator_options["Измерение времени"] = True
        return self

    def add_memory_decorator(self):
        """Добавляет декоратор функций памяти"""
        self.decorator_options["Память"] = True
        self.add_buttons(['MS', 'MR', 'M+', 'MC'])
        return self
    
    def add_precision_decorator(self, precision=5):
        """Добавляет декоратор настраиваемой точности"""
        self.decorator_options["Настраиваемая точность"] = True
        self.precision_value = precision
        return self

    def build(self):
        """Создает и возвращает итоговый объект"""
        return self.options, self.history_options, self.buttons, self.decorator_options, self.precision_value