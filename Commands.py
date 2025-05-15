# commands.py
class ICommand:
    def execute(self):
        raise NotImplementedError()

class CalculateCommand(ICommand):
    def __init__(self, calculator, expression, model):
        self.calculator = calculator
        self.expression = expression
        self.model = model
        self.result = None

    def execute(self):
        self.result = self.calculator.calculate(self.expression)
        self.model.save_to_history(self.expression)
        return self.result

class MemoryStoreCommand(ICommand):
    def __init__(self, memory_decorator, value):
        self.memory_decorator = memory_decorator
        self.value = value

    def execute(self):
        self.memory_decorator.memory_store(self.value)

class MemoryClearCommand(ICommand):
    def __init__(self, memory_decorator):
        self.memory_decorator = memory_decorator

    def execute(self):
        self.memory_decorator.memory_clear()
