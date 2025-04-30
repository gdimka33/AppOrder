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
        self.pack(fill='both', expand=True)
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
        
        # Размещаем элементы
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Загружаем данные
        self._загрузить_посты()
    
    def _загрузить_посты(self):
        """Загружает список постов из базы данных и создает для каждого виджет ПостНаряда"""
        try:
            запрос = """
                SELECT 
                    id,
                    наименование,
                    дежурный_кол,
                    дежурный_офицер,
                    дневальный_кол
                FROM посты
                ORDER BY id
            """
            результат = выполнить_запрос(запрос)
            
            # Создаем виджет для каждого поста
            for пост in результат:
                пост_наряда = ПостНаряда(
                    self.scrollable_frame,
                    пост_ид=пост['id'],
                    дата_наряда=self.дата_наряда,
                    подразделение="",  # Подразделение будет установлено позже
                    style="Duty.TFrame"
                )
                пост_наряда.pack(fill='x', padx=5, pady=2)
                
            logger.info("Список постов успешно загружен")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке списка постов: {e}")
            self._показать_ошибку(f"Ошибка при загрузке списка постов: {e}")
    
    def _показать_ошибку(self, текст_ошибки):
        """Отображает информационное окно с ошибкой"""
        форматированный_текст = [
            ("Ошибка при получении данных!\n\n", ["header", "red"]),
            ("Детали ошибки:\n", ["bold"]),
            (текст_ошибки, ["red"])
        ]
        ИнформационноеОкно(self, форматированный_текст)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Состав наряда")
    root.geometry("800x600")
    
    app = СоставНаряда(root)
    app.pack(fill='both', expand=True)
    
    root.mainloop()