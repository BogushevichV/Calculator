import tkinter as tk
from Controller import CalculatorController

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorController(root)
    root.mainloop()