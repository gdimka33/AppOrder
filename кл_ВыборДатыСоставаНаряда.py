import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
from logger import logger

class ВыборДатыСоставаНаряда(ttk.Frame):
    """
    Класс для выбора дат для состава наряда.
    Отображает календарь с возможностью выбора нескольких дат.
    """
    def __init__(self, родитель, callback=None):
        """Инициализация класса"""
        super().__init__(родитель)
        self.master = родитель
        self.callback = callback  # Сохраняем callback-функцию
        
        # Создаем основной фрейм для размещения календаря и кнопок
        self.основной_фрейм = ttk.Frame(self)
        self.основной_фрейм.pack(side='left', fill='both', padx=5, pady=5)
        
        # Инициализация переменных
        self.текущая_дата = datetime.now()
        self.выбранные_даты = set()  # Используем множество для хранения выбранных дат
        
        # Создаем элементы интерфейса внутри основного фрейма
        self._создать_элементы()
        
        # Заполняем календарь
        self._обновить_календарь()
        
        # Обновляем список выбранных дат
        self._обновить_список_дат()
    
    def _создать_элементы(self):
        """Создает основные элементы интерфейса"""
        # Создаем фрейм для календаря
        self.календарь_фрейм = ttk.Frame(self)
        self.календарь_фрейм.pack(fill='x', padx=5, pady=5)
        
        # Создаем верхнюю панель с навигацией по месяцам
        панель_навигации = ttk.Frame(self.календарь_фрейм)
        панель_навигации.pack(fill='x', pady=5)
        
        # Кнопки навигации и метка с текущим месяцем
        self.кнопка_предыдущий = ttk.Button(
            панель_навигации, 
            text="←", 
            width=3,
            command=self._предыдущий_месяц
        )
        self.кнопка_предыдущий.pack(side='left', padx=5)
        
        self.метка_месяц = ttk.Label(
            панель_навигации,
            width=20,
            anchor='center'
        )
        self.метка_месяц.pack(side='left', expand=True)
        
        self.кнопка_следующий = ttk.Button(
            панель_навигации,
            text="→",
            width=3,
            command=self._следующий_месяц
        )
        self.кнопка_следующий.pack(side='right', padx=5)
        
        # Создаем фрейм для дней недели и календарной сетки
        self.сетка_календаря = ttk.Frame(self.календарь_фрейм)
        self.сетка_календаря.pack(fill='both', expand=True)
        
        # Создаем метки для дней недели
        дни_недели = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for i, день in enumerate(дни_недели):
            ttk.Label(
                self.сетка_календаря,
                text=день,
                width=4,
                anchor='center'
            ).grid(row=0, column=i, padx=1, pady=1)
        
        # Создаем фрейм для списка выбранных дат
        self.фрейм_списка = ttk.LabelFrame(self, text="Выбранные даты")
        self.фрейм_списка.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем список для отображения выбранных дат
        self.список_дат = tk.Text(
            self.фрейм_списка,
            height=5,
            width=30,
            state='disabled'
        )
        self.список_дат.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем стили для кнопок
        style = ttk.Style()
        style.configure(
            "CurrentDay.TButton",
            background="#E6F3FF",
            foreground="#000000"
        )
        # Добавляем маппинг для состояний кнопки
        style.map(
            "CurrentDay.TButton",
            background=[
                ("pressed", "#CCE4FF"),
                ("active", "#E6F3FF")
            ],
            relief=[("pressed", "sunken")]
        )

    def _обновить_календарь(self):
        """Обновляет отображение календаря"""
        # Обновляем метку с текущим месяцем и годом
        месяц_год = self.текущая_дата.strftime("%B %Y").capitalize()
        self.метка_месяц.configure(text=месяц_год)
        
        # Очищаем существующие кнопки дат
        for виджет in self.сетка_календаря.winfo_children():
            if isinstance(виджет, ttk.Button):
                виджет.destroy()
        
        # Получаем календарь на текущий месяц
        календарь_месяца = calendar.monthcalendar(
            self.текущая_дата.year,
            self.текущая_дата.month
        )
        
        # Получаем сегодняшнюю дату для сравнения
        сегодня = datetime.now().date()
        
        # Создаем кнопки для каждого дня
        for номер_недели, неделя in enumerate(календарь_месяца, 1):
            for день_недели, день in enumerate(неделя):
                if день != 0:
                    дата = datetime(
                        self.текущая_дата.year,
                        self.текущая_дата.month,
                        день
                    )
                    
                    # Определяем стиль кнопки и дополнительные параметры
                    if дата.date() == сегодня:
                        стиль = "CurrentDay.TButton"
                    else:
                        стиль = "TButton"
                    
                    # Создаем кнопку для даты
                    кнопка = ttk.Button(
                        self.сетка_календаря,
                        text=str(день),
                        width=4,
                        style=стиль,
                        command=lambda d=дата: self._переключить_выбор_даты(d)
                    )
                    кнопка.grid(
                        row=номер_недели,
                        column=день_недели,
                        padx=1,
                        pady=1
                    )
                    
                    # Если дата выбрана, применяем состояние pressed
                    if дата in self.выбранные_даты:
                        кнопка.state(['pressed'])
    
    def _переключить_выбор_даты(self, дата):
        """Обрабатывает выбор/отмену выбора даты"""
        if дата in self.выбранные_даты:
            self.выбранные_даты.remove(дата)
        else:
            self.выбранные_даты.add(дата)
        
        # Обновляем отображение календаря и списка дат
        self._обновить_календарь()
        self._обновить_список_дат()
        
    def _обновить_список_дат(self):
        """Обновляет список выбранных дат и создает кнопки"""
        # Очищаем текущие кнопки
        for виджет in self.фрейм_списка.winfo_children():
            виджет.destroy()
        
        # Сортируем даты
        отсортированные_даты = sorted(self.выбранные_даты)
        
        # Создаем кнопки для каждой даты
        for дата in отсортированные_даты:
            следующая_дата = дата + timedelta(days=1)
            текст_кнопки = f"{дата.strftime('%d.%m.%Y')} - {следующая_дата.strftime('%d.%m.%Y')}"
            
            кнопка = ttk.Button(
                self.фрейм_списка,
                text=текст_кнопки,
                command=lambda д=дата: self._показать_состав_наряда(д)
            )
            кнопка.pack(fill='x', padx=5, pady=2)
    
    def _показать_состав_наряда(self, дата):
        """Вызывает callback-функцию для отображения состава наряда"""
        if self.callback:
            self.callback(дата)

    def _предыдущий_месяц(self):
        """Переход к предыдущему месяцу"""
        self.текущая_дата = self.текущая_дата.replace(day=1) - timedelta(days=1)
        self.текущая_дата = self.текущая_дата.replace(day=1)
        self._обновить_календарь()
    
    def _следующий_месяц(self):
        """Переход к следующему месяцу"""
        if self.текущая_дата.month == 12:
            self.текущая_дата = self.текущая_дата.replace(
                year=self.текущая_дата.year + 1,
                month=1,
                day=1
            )
        else:
            self.текущая_дата = self.текущая_дата.replace(
                month=self.текущая_дата.month + 1,
                day=1
            )
        self._обновить_календарь()
    
    def получить_выбранные_даты(self):
        """Возвращает список выбранных дат"""
        return sorted(list(self.выбранные_даты))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Выбор даты")
    root.geometry("300x400")
    
    выбор_дат = ВыборДатыСоставаНаряда(root)
    выбор_дат.pack(fill='both', expand=True, padx=10, pady=10)
    
    root.mainloop()