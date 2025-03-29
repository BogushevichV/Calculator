class CalculatorBuilder:
    """Строитель калькулятора, отвечает за поэтапное добавление функций"""

    def __init__(self):
        self.options = {
            "Научные функции": False,
            "Программные операции": False,
            "Инженерные операции": False
        }
        self.buttons = [['7', '8', '9', '/'],
                        ['4', '5', '6', '*'],
                        ['1', '2', '3', '-'],
                        ['C', '0', '=', '+'],
                        ['.', '(', ')']]

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

    def build(self):
        """Создает и возвращает итоговый объект"""
        return self.options, self.buttons