# Decorator.py
import time
import os
from datetime import datetime
from abc import ABC, abstractmethod


class ICalculator(ABC):
    """Интерфейс для калькулятора и декораторов"""
    
    @abstractmethod
    def calculate(self, expression):
        """Вычисляет выражение и возвращает результат"""
        pass


class CalculatorDecorator(ICalculator):
    """Базовый класс для всех декораторов калькулятора"""
    
    def __init__(self, calculator):
        self._calculator = calculator
        
    def calculate(self, expression):
        return self._calculator.calculate(expression)


class TimingDecorator(CalculatorDecorator):
    """Декоратор для измерения времени выполнения вычислений"""
    
    def __init__(self, calculator):
        super().__init__(calculator)
        self.last_execution_time = 0
        
    def calculate(self, expression):
        start_time = time.time()
        result = self._calculator.calculate(expression)
        end_time = time.time()
        
        self.last_execution_time = end_time - start_time
        
        return result
    
    def get_last_execution_time(self):
        """Возвращает время выполнения последнего вычисления в миллисекундах"""
        return self.last_execution_time * 1000


class MemoryDecorator(CalculatorDecorator):
    """Декоратор для добавления функций памяти в калькулятор"""
    
    def __init__(self, calculator):
        super().__init__(calculator)
        self.memory = 0
        
    def calculate(self, expression):
        # Заменяем обращения к памяти в выражении
        expression = expression.replace("MR", str(self.memory))
        return self._calculator.calculate(expression)
    
    def memory_store(self, value):
        """Сохраняет значение в памяти"""
        try:
            self.memory = float(value)
        except ValueError:
            # Если значение не числовое, пытаемся вычислить его
            try:
                self.memory = float(self._calculator.calculate(value))
            except Exception:
                raise ValueError("Невозможно сохранить значение в памяти")
    
    def memory_recall(self):
        """Возвращает значение из памяти"""
        return self.memory
    
    def memory_add(self, value):
        """Добавляет значение к памяти"""
        try:
            self.memory += float(value)
        except ValueError:
            try:
                self.memory += float(self._calculator.calculate(value))
            except Exception:
                raise ValueError("Невозможно добавить значение к памяти")
    
    def memory_clear(self):
        """Очищает память"""
        self.memory = 0


class PrecisionDecorator(CalculatorDecorator):
    """Декоратор для установки точности результатов вычислений"""
    
    def __init__(self, calculator, precision=5):
        super().__init__(calculator)
        self.precision = precision
    
    def calculate(self, expression):
        result = self._calculator.calculate(expression)
        
        # Округляем результат до указанной точности
        if isinstance(result, (int, float)):
            return round(result, self.precision)
        
        return result
    
    def set_precision(self, precision):
        """Устанавливает новую точность вычислений"""
        self.precision = precision