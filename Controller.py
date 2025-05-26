# Controller.py
from Commands import CalculateCommand, MemoryClearCommand, MemoryStoreCommand
from Model import CalculatorModel
from View import CalculatorView
from Builder import CalculatorBuilder
from Decorator import TimingDecorator, MemoryDecorator, PrecisionDecorator

from tkinter import filedialog, simpledialog


class CalculatorController:
    """Контроллер калькулятора - связывает модель и представление"""

    def __init__(self, root):
        self.builder = CalculatorBuilder()

        self.options, self.history_options, self.buttons, self.decorator_options, self.precision_value = self.builder.build()

        # Создаем базовую модель
        self.base_model = CalculatorModel(self.options, self.history_options)
        
        # Применяем декораторы в соответствии с настройками
        self.calculator = self.apply_decorators(self.base_model)
        
        self.view = CalculatorView(root, self, self.history_options, self.options, self.buttons, self.decorator_options)

    def apply_decorators(self, model):
        """Применяет выбранные декораторы к модели"""
        calculator = model
        
        # Применяем декораторы в соответствии с настройками
        if self.decorator_options["Настраиваемая точность"]:
            calculator = PrecisionDecorator(calculator, self.precision_value)
            
        if self.decorator_options["Измерение времени"]:
            calculator = TimingDecorator(calculator)
            
        if self.decorator_options["Память"]:
            calculator = MemoryDecorator(calculator)
            
        return calculator

    def update_options(self, selected_options, selected_history_options, selected_decorator_options=None, precision_value=5):
        """Обновляет функционал через Builder"""
        self.builder = CalculatorBuilder()  # Новый Строитель

        # Применяем выбранные опции

        if selected_options["Научные функции"]:
            self.builder.add_scientific_functions()
        if selected_options["Программные операции"]:
            self.builder.add_programming_operations()
        if selected_options["Инженерные операции"]:
            self.builder.add_engineering_operations()

        self.builder.toggle_history_saving(selected_history_options["Сохранение выражений"])
        
        # Применяем декораторы
        if selected_decorator_options:
            if selected_decorator_options["Измерение времени"]:
                self.builder.add_timing_decorator()
            if selected_decorator_options["Память"]:
                self.builder.add_memory_decorator()
            if selected_decorator_options["Настраиваемая точность"]:
                self.builder.add_precision_decorator(precision_value)

        # Получаем обновленные настройки
        self.options, self.history_options, self.buttons, self.decorator_options, self.precision_value = self.builder.build()
        
        # Обновляем модель и применяем декораторы
        self.base_model.update_options(self.options)
        self.base_model.update_history_options(self.history_options)
        self.calculator = self.apply_decorators(self.base_model)
        
        # Обновляем представление
        self.view.update_buttons(self.options, self.buttons)
        self.view.update_decorator_options(self.decorator_options)

    def on_button_click(self, char):

        if char == "C":
            self.view.clear_entry()
        elif char == "=":
            try:
                expression = self.view.get_entry_text()
                command = CalculateCommand(self.calculator, expression, self.base_model)
                result = command.execute()#self.calculator.calculate(expression)
                self.base_model.save_to_history(expression)
                
                # Если включен декоратор измерения времени, показываем информацию о времени
                if self.decorator_options["Измерение времени"]:
                    execution_time = None
                    # Ищем TimingDecorator в цепочке декораторов
                    current = self.calculator
                    while hasattr(current, '_calculator'):
                        if isinstance(current, TimingDecorator):
                            execution_time = current.get_last_execution_time()
                            break
                        current = current._calculator
                    
                    if execution_time is not None:
                        self.view.show_execution_time(execution_time)
                
                self.view.set_entry_text(str(result))
            except Exception as ex:
                print(ex)
                self.view.set_entry_text("Ошибка")
        elif char in ["sin", "cos", "tan", "cot"]:
            self.view.insert_text(f"{char}(")
        elif char == "^":
            self.view.insert_text("^")
        # Обработка кнопок памяти
        elif char == "MS" and self.decorator_options["Память"]:
            try:
                value = self.view.get_entry_text()
                # Ищем MemoryDecorator в цепочке декораторов
                decorator = self.find_decorator(MemoryDecorator)
                if decorator:
                    command = MemoryStoreCommand(decorator, value)
                    command.execute()
                    self.view.show_memory_status("Сохранено в памяти")
            except Exception as ex:
                print(ex)
                self.view.show_memory_status("Ошибка сохранения")
        elif char == "MR" and self.decorator_options["Память"]:
            # Ищем MemoryDecorator в цепочке декораторов
            current = self.calculator
            while hasattr(current, '_calculator'):
                if isinstance(current, MemoryDecorator):
                    value = current.memory_recall()
                    self.view.insert_text(str(value))
                    break
                current = current._calculator
        elif char == "M+" and self.decorator_options["Память"]:
            try:
                value = self.view.get_entry_text()
                # Ищем MemoryDecorator в цепочке декораторов
                current = self.calculator
                while hasattr(current, '_calculator'):
                    if isinstance(current, MemoryDecorator):
                        current.memory_add(value)
                        self.view.show_memory_status("Добавлено к памяти")
                        break
                    current = current._calculator
            except Exception as ex:
                print(ex)
                self.view.show_memory_status("Ошибка добавления")
        elif char == "MC" and self.decorator_options["Память"]:
            # Ищем MemoryDecorator в цепочке декораторов
            decorator = self.find_decorator(MemoryDecorator)
            if decorator:
                command = MemoryClearCommand(decorator)
                command.execute()
                self.view.show_memory_status("Память очищена")
        else:
            self.view.insert_text(char)

    def show_history(self):
        history = self.base_model.get_history()
        self.view.show_history_window(history)

    def find_decorator(self, decorator_type):
        current = self.calculator
        while hasattr(current, '_calculator'):
            if isinstance(current, decorator_type):
                return current
            current = current._calculator
        return None


    def change_history_limit(self):
        """Изменяет лимит истории"""
        new_limit = simpledialog.askinteger("Лимит истории", 
                                          "Введите новый лимит истории:",
                                          initialvalue=self.history_options["Лимит истории"],
                                          minvalue=1, maxvalue=1000)
        if new_limit:
            self.history_options["Лимит истории"] = new_limit
            self.base_model.update_history_options(self.history_options)


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
            self.base_model.update_history_options(self.history_options)

    def insert_from_history(self, expression):

        self.view.set_entry_text(expression.strip())

    def change_precision(self):
        """Изменяет точность вычислений"""
        new_precision = simpledialog.askinteger("Точность", 
                                         "Введите новую точность вычислений (количество знаков после запятой):",
                                         initialvalue=self.precision_value,
                                         minvalue=0, maxvalue=15)
        if new_precision is not None:
            self.precision_value = new_precision
            # Обновляем декоратор точности
            self.update_options(
                self.options, 
                self.history_options, 
                self.decorator_options,
                self.precision_value,
            )
            self.view.show_status_message(f"Точность установлена: {new_precision} знаков")

    @staticmethod
    def on_key_press(event):
        """Обрабатывает нажатие клавиш"""
        allowed_keys = "0123456789+-*/.=acdegilmnoprstx()^√"

        if event.char not in allowed_keys and event.keysym not in ["BackSpace", "Return", "Tab", "Left", "Right"]:
            return "break"