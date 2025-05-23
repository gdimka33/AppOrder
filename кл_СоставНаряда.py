import tkinter as tk
from tkinter import ttk
from datetime import datetime
from БД_соединение import выполнить_запрос
from logger import logger
from кл_ИнформационноеОкно import ИнформационноеОкно
from кл_ПостНаряда import ПостНаряда

class СоставНаряда(ttk.Frame):
    """Класс для отображения списка постов наряда"""
    
    def __init__(self, родитель, дата_наряда: datetime = None):
        super().__init__(родитель)
        self.pack(side="top", fill='both', expand=True)
        self.дата_наряда = дата_наряда or datetime.now()
        
        # Создаем канвас и фрейм для прокрутки
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Настраиваем прокрутку
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Привязываем прокрутку к колесику мыши
        self._привязать_прокрутку(self.canvas)
        self._привязать_прокрутку(self.scrollable_frame)
        
        # Размещаем элементы
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Загружаем данные
        self._загрузить_посты()
    
    def _привязать_прокрутку(self, виджет):
        """Привязывает обработчик прокрутки к виджету и всем его дочерним элементам"""
        виджет.bind("<MouseWheel>", self._прокрутка_мышью)
        виджет.bind("<Button-4>", self._прокрутка_мышью)  # Для Linux
        виджет.bind("<Button-5>", self._прокрутка_мышью)  # Для Linux
        
        # Для всех дочерних виджетов тоже привязываем прокрутку
        for дочерний in виджет.winfo_children():
            self._привязать_прокрутку(дочерний)

    def _загрузить_посты(self):
        """Загружает список постов из базы данных и создает для каждого виджет ПостНаряда"""
        try:
            # Проверяем существование таблицы постов
            таблица_существует = выполнить_запрос("SELECT name FROM sqlite_master WHERE type='table' AND name='посты'")
            if not таблица_существует:
                logger.error("Таблица 'посты' не существует в базе данных")
                self._показать_ошибку("Таблица постов не найдена. Запустите БД_заполнение_при_создании.py")
                return
                
            запрос = "SELECT id, наименование FROM посты ORDER BY id"
            результат = выполнить_запрос(запрос)
            
            if not результат:
                logger.warning("Таблица постов пуста")
                self._показать_ошибку("Таблица постов пуста. Заполните таблицу через БД_заполнение_при_создании.py")
                return
                
            # Очищаем предыдущие виджеты
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            # Создаем виджет для каждого поста
            for пост in результат:
                try:
                    пост_наряда = ПостНаряда(
                        self.scrollable_frame,
                        пост_ид=пост['id'],
                        дата_наряда=self.дата_наряда,
                        подразделение=""
                    )
                    пост_наряда.pack(fill='x', padx=5, pady=2)
                    
                    # Привязываем прокрутку к новому виджету
                    self._привязать_прокрутку(пост_наряда)
                    
                    # Обновляем канвас после добавления каждого виджета
                    self.canvas.update_idletasks()
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    
                except Exception as e:
                    logger.error(f"Ошибка создания виджета для поста {пост.get('id', 'N/A')}: {e}")
                    continue
                
            logger.info(f"Успешно загружено {len(результат)} постов")
            
        except Exception as e:
            logger.error(f"Критическая ошибка при загрузке постов: {e}")
            self._показать_ошибку(f"Не удалось загрузить список постов: {e}")
    
    def _показать_ошибку(self, текст_ошибки):
        """Отображает информационное окно с ошибкой"""
        форматированный_текст = [
            ("Ошибка при получении данных!\n\n", ["header", "red"]),
            ("Детали ошибки:\n", ["bold"]),
            (текст_ошибки, ["red"])
        ]
        ИнформационноеОкно(self, форматированный_текст)

    def _прокрутка_мышью(self, event):
        """Обработчик прокрутки колесиком мыши"""
        if event.num == 5 or event.delta < 0:  # Прокрутка вниз
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Прокрутка вверх
            self.canvas.yview_scroll(-1, "units")
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Состав наряда")
    root.geometry("800x600")
    
    app = СоставНаряда(root)
    app.pack(fill='both', expand=True)
    
    root.mainloop()