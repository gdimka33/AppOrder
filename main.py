import tkinter as tk
from tkinter import ttk
from logger import logger
from БД_соединение import создание_базыданных
from кл_СписокСотрудников import СписокСотрудников
from кл_ПриказСуточныйНаряд import ПриказСуточныйНаряд


# Пример использования:
logger.info('Приложение запущено')
# Инициализация базы данных
создание_базыданных()

class ГлавноеОкно(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учет личного состава")
        
        # Разворачиваем окно на весь экран
        self.state('zoomed')
        
        # Устанавливаем начальный размер окна
        self.geometry("800x600")
        
        # Создаем фреймы
        self.левый_фрейм = ttk.Frame(self, width=200, style='Left.TFrame')
        self.центральный_фрейм = ttk.Frame(self, width=200)
        
        # Располагаем фреймы
        self.левый_фрейм.pack(side='left', fill='y')
        self.центральный_фрейм.pack(side='left', fill='both', expand=True)
        
        # Удаляем старые кнопки и добавляем группы
        # Создаем группу Приказы
        группа_приказы = ttk.LabelFrame(self.левый_фрейм, text="Приказы", padding=10)
        группа_приказы.pack(fill='x', pady=5, padx=5)
        
        ttk.Button(группа_приказы, text="Новый суточный приказ", 
                  command=self.показать_суточный_приказ).pack(pady=2, fill='x')
        ttk.Button(группа_приказы, text="Приказ внесения изменений").pack(pady=2, fill='x')

        # Создаем группу Списки сотрудников
        группа_списки = ttk.LabelFrame(self.левый_фрейм, text="Списки сотрудников", padding=10)
        группа_списки.pack(fill='x', pady=5, padx=5)
        
        # Создаем кнопки и привязываем к ним обработчики
        ttk.Button(группа_списки, text="Список офицеров", 
                  command=lambda: self.показать_список_сотрудников("офицер")).pack(pady=2, fill='x')
        ttk.Button(группа_списки, text="Список курсантов", 
                  command=lambda: self.показать_список_сотрудников("курсант")).pack(pady=2, fill='x')

        # Обновляем размеры окна после создания всех виджетов
        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), 600)  # Минимальная высота 600
        self._center_window()  # Центрируем окно

    def _center_window(self):
        """Центрирует окно на экране, сохраняя текущие размеры"""
        # Нет необходимости центрировать, если окно развернуто на весь экран
        pass

    def показать_список_сотрудников(self, тип_сотрудника):
        """Отображает список сотрудников в центральном фрейме"""
        # Очищаем центральный фрейм
        for виджет in self.центральный_фрейм.winfo_children():
            виджет.destroy()
        
        # Создаем и отображаем список сотрудников
        СписокСотрудников(self.центральный_фрейм, тип_сотрудника, self)
        
        # Обновляем размер окна после добавления нового контента
        self.update_idletasks()
        # Сначала обновляем размеры, затем центрируем
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_height()}")
        self._center_window()
        
    def показать_суточный_приказ(self):
        """Отображает форму создания суточного приказа в центральном фрейме"""
        # Очищаем центральный фрейм
        for виджет in self.центральный_фрейм.winfo_children():
            виджет.destroy()
        
        # Создаем и отображаем форму суточного приказа
        ПриказСуточныйНаряд(self.центральный_фрейм, self)
        
        # Обновляем размер окна после добавления нового контента
        self.update_idletasks()
        # Сначала обновляем размеры, затем центрируем
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_height()}")
        self._center_window()


if __name__ == "__main__":
    app = ГлавноеОкно()
    app.mainloop()
