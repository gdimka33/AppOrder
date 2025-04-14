import tkinter as tk
from tkinter import ttk
from logger import logger
from БД_соединение import создание_базыданных
from кл_Список_сотрудников import СписокСотрудников


# Пример использования:
logger.info('Приложение запущено')
# Инициализация базы данных
создание_базыданных()

class ГлавноеОкно(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учет личного состава")
        
        # Размер окна
        минимальная_ширина_окна = 800
        высота_окна = 600
        
        # Центрируем окно на экране
        ширина_экрана = self.winfo_screenwidth()
        высота_экрана = self.winfo_screenheight()
        x = (ширина_экрана - минимальная_ширина_окна) // 2
        y = (высота_экрана - высота_окна) // 2
        self.geometry(f"{минимальная_ширина_окна}x{высота_окна}+{x}+{y}")
        
        # Устанавливаем минимальный размер окна
        self.minsize(минимальная_ширина_окна, высота_окна)
        
        # Разрешаем окну изменять размер в соответствии с содержимым
        self.pack_propagate(True)

        # Создаем три фрейма
        self.левый_фрейм = ttk.Frame(self, width=200, style='Left.TFrame')
        self.центральный_фрейм = ttk.Frame(self)
        
        # Располагаем фреймы слева направо
        self.левый_фрейм.pack(side='left', fill='y')
        self.центральный_фрейм.pack(side='left', fill='both', expand=True)

        # Удаляем старые кнопки и добавляем группы
        # Создаем группу Приказы
        группа_приказы = ttk.LabelFrame(self.левый_фрейм, text="Приказы", padding=10)
        группа_приказы.pack(fill='x', pady=5, padx=5)
        
        ttk.Button(группа_приказы, text="Новый суточный приказ").pack(pady=2, fill='x')
        ttk.Button(группа_приказы, text="Приказ внесения изменений").pack(pady=2, fill='x')

        # Создаем группу Списки сотрудников
        группа_списки = ttk.LabelFrame(self.левый_фрейм, text="Списки сотрудников", padding=10)
        группа_списки.pack(fill='x', pady=5, padx=5)
        
        # Создаем кнопки и привязываем к ним обработчики
        ttk.Button(группа_списки, text="Список офицеров", 
                  command=lambda: self.показать_список_сотрудников("офицер")).pack(pady=2, fill='x')
        ttk.Button(группа_списки, text="Список курсантов", 
                  command=lambda: self.показать_список_сотрудников("курсант")).pack(pady=2, fill='x')


    def показать_список_сотрудников(self, тип_сотрудника):
        """Отображает список сотрудников в центральном фрейме"""
        # Очищаем центральный фрейм
        for виджет in self.центральный_фрейм.winfo_children():
            виджет.destroy()
        
        # Создаем и отображаем список сотрудников, передавая ссылку на главное окно
        СписокСотрудников(self.центральный_фрейм, тип_сотрудника, self)


if __name__ == "__main__":
    app = ГлавноеОкно()
    app.mainloop()
