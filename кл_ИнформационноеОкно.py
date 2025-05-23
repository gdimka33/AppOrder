import tkinter as tk
from tkinter import ttk
from logger import logger

class ИнформационноеОкно(ttk.Frame):
    """
    Класс для отображения информационного окна с форматированным текстом.
    """
    def __init__(self, родитель, информация, тип_окна="информация", callback=None, форматирование=None):
        """
        Инициализация информационного окна
        
        Args:
            родитель: Родительский виджет, в котором будет отображаться окно
            информация: Текст для отображения
            тип_окна: Тип окна (информация, подтверждение, ок)
            callback: Функция обратного вызова для кнопок
            форматирование: Словарь с параметрами форматирования текста
        """
        super().__init__(родитель)
        self.родитель = родитель
        self.информация = информация
        self.тип_окна = тип_окна
        self.callback = callback
        self.форматирование = форматирование or {}
        
        # Растягиваем фрейм на всю ширину и высоту родительского контейнера
        self.pack(fill='both', expand=True)
        
        # Создаем содержимое окна
        self._создать_содержимое()
        
        logger.info(f"Отображено информационное окно типа: {тип_окна}")
    
    def _создать_содержимое(self):
        """Создает содержимое информационного окна"""
        # Создаем фрейм для содержимого с отступами
        фрейм_содержимого = ttk.Frame(self, padding=20)
        фрейм_содержимого.pack(fill='both', expand=True)
        
        # Создаем левый фрейм для текста
        фрейм_текста = ttk.Frame(фрейм_содержимого)
        фрейм_текста.pack(side='left', fill='both', expand=True)
        
        # Добавляем текст информации с поддержкой форматирования
        self.текст = tk.Text(фрейм_текста, wrap='word', height=10, width=50)
        
        # Настраиваем теги форматирования
        self._настроить_форматирование()
        
        # Вставляем текст с форматированием
        self._вставить_форматированный_текст()
        
        # Делаем текст только для чтения
        self.текст.config(state='disabled')
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(фрейм_текста, command=self.текст.yview)
        self.текст.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем текст и скроллбар
        scrollbar.pack(side='right', fill='y')
        self.текст.pack(side='left', fill='both', expand=True, pady=10)
        
        # Добавляем кнопки в зависимости от типа окна (справа от текста)
        фрейм_кнопок = ttk.Frame(фрейм_содержимого, padding=(10, 0, 0, 0))
        фрейм_кнопок.pack(side='right', fill='y', padx=5)
        
        if self.тип_окна == "информация":
            # Только кнопка ОК
            ttk.Button(фрейм_кнопок, text="ОК", 
                      command=self._закрыть_окно).pack(padx=5, pady=5)
            
        elif self.тип_окна == "подтверждение":
            # Кнопки Подтвердить и Отменить
            ttk.Button(фрейм_кнопок, text="Подтвердить", 
                      command=lambda: self._обработать_действие(True)).pack(padx=5, pady=5)
            ttk.Button(фрейм_кнопок, text="Отменить", 
                      command=lambda: self._обработать_действие(False)).pack(padx=5, pady=5)
            
        elif self.тип_окна == "ок":
            # Только кнопка ОК с обратным вызовом
            ttk.Button(фрейм_кнопок, text="ОК", 
                      command=lambda: self._обработать_действие(True)).pack(padx=5, pady=5)
    
    def _настроить_форматирование(self):
        """Настраивает теги форматирования для текста"""
        # Стандартные теги форматирования
        self.текст.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.текст.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        self.текст.tag_configure("underline", underline=True)
        self.текст.tag_configure("header", font=("TkDefaultFont", 12, "bold"))
        self.текст.tag_configure("red", foreground="red")
        self.текст.tag_configure("blue", foreground="blue")
        self.текст.tag_configure("green", foreground="green")
        
        # Пользовательские теги форматирования
        for тег, параметры in self.форматирование.items():
            self.текст.tag_configure(тег, **параметры)
    
    def _вставить_форматированный_текст(self):
        """Вставляет форматированный текст"""
        # Если информация - это строка, вставляем как обычный текст
        if isinstance(self.информация, str):
            self.текст.insert("1.0", self.информация)
        
        # Если информация - это список кортежей (текст, [теги]), применяем форматирование
        elif isinstance(self.информация, list):
            for текст, теги in self.информация:
                индекс = self.текст.index("end-1c")
                self.текст.insert("end", текст)
                
                # Применяем теги к вставленному тексту
                if теги:
                    конец = self.текст.index("end-1c")
                    for тег in теги:
                        self.текст.tag_add(тег, индекс, конец)
    
    def _закрыть_окно(self):
        """Закрывает информационное окно"""
        self.destroy()
    
    def _обработать_действие(self, результат):
        """Обрабатывает действие пользователя и вызывает callback"""
        if self.callback:
            self.callback(результат)
        self._закрыть_окно()

# Пример использования:
# Простой текст:
# информационное_окно = ИнформационноеОкно(родитель, "Текст сообщения")

# Форматированный текст:
# форматированный_текст = [
#     ("Заголовок\n", ["header"]),
#     ("Обычный текст, ", []),
#     ("жирный текст, ", ["bold"]),
#     ("красный текст, ", ["red"]),
#     ("жирный красный текст", ["bold", "red"])
# ]
# информационное_окно = ИнформационноеОкно(родитель, форматированный_текст)

# Пользовательское форматирование:
# пользовательское_форматирование = {
#     "custom1": {"font": ("Arial", 12, "bold"), "foreground": "#336699"},
#     "custom2": {"background": "yellow", "relief": "raised"}
# }
# информационное_окно = ИнформационноеОкно(родитель, форматированный_текст, 
#                                          форматирование=пользовательское_форматирование)