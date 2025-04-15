import tkinter as tk
from tkinter import ttk
from БД_соединение import выполнить_запрос
from logger import logger

class ПоискОфицера(ttk.Frame):
    """
    Виджет для поиска офицеров по фамилии.
    Представляет собой комбобокс с функцией посимвольного поиска.
    """
    def __init__(self, родитель, callback=None, placeholder="Введите фамилию для поиска..."):
        super().__init__(родитель)

        self.callback = callback
        self.placeholder = placeholder
        self.результаты_поиска = []
        
        # Создаем основной контейнер
        self.pack(fill='x', expand=True)
        
        # Создаем комбобокс
        self.combobox = ttk.Combobox(self)
        self.combobox.pack(fill='x', padx=5, pady=5)
        self.combobox['values'] = []
        self.combobox.set(self.placeholder)
        self.combobox.config(foreground='gray')
        
        # Привязываем обработчики событий
        self.combobox.bind("<FocusIn>", self._on_focus_in)
        self.combobox.bind("<FocusOut>", self._on_focus_out)
        self.combobox.bind("<KeyRelease>", self._on_key_release)
        self.combobox.bind("<<ComboboxSelected>>", self._on_item_selected)
    
    def _on_focus_in(self, event):
        """Обработчик получения фокуса полем ввода"""
        if self.combobox.get() == self.placeholder:
            self.combobox.set('')
            self.combobox.config(foreground='black')
    
    def _on_focus_out(self, event):
        """Обработчик потери фокуса полем ввода"""
        if not self.combobox.get():
            self.combobox.set(self.placeholder)
            self.combobox.config(foreground='gray')
    
    def _on_key_release(self, event):
        """Обработчик ввода текста в поле поиска"""
        # Игнорируем специальные клавиши
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
            return
        
        # Получаем текущий текст поиска
        текст_поиска = self.combobox.get().strip()
        
        # Если текст не пустой и не равен placeholder, выполняем поиск
        if текст_поиска and текст_поиска != self.placeholder:
            self._выполнить_поиск(текст_поиска)
        else:
            # Очищаем список значений
            self.combobox['values'] = []
    
    def _выполнить_поиск(self, текст_поиска):
        """Выполняет поиск офицеров по введенной фамилии"""
        try:
            # Формируем запрос к базе данных
            запрос = """
                SELECT о.id, о.фамилия, о.имя, о.отчество, з.наименование as звание, д.наименование as должность
                FROM офицеры о
                LEFT JOIN звания з ON о.звание_id = з.id
                LEFT JOIN должности д ON о.должность_id = д.id
                WHERE о.фамилия LIKE ?
                ORDER BY о.фамилия, о.имя
            """
            параметры = (f"{текст_поиска}%",)
            
            # Выполняем запрос
            результат = выполнить_запрос(запрос, параметры)
            
            # Очищаем список результатов
            self.результаты_поиска = []
            values = []
            
            if результат:
                # Заполняем список результатов
                for офицер in результат:
                    фио = f"{офицер['фамилия']} {офицер['имя'][0]}.{офицер['отчество'][0] if офицер['отчество'] else ''}"
                    должность = офицер['должность'] if офицер['должность'] else "Должность не указана"
                    звание = офицер['звание'] if офицер['звание'] else "Звание не указано"
                    
                    отображение = f"{звание} {фио} - {должность}"
                    values.append(отображение)
                    self.результаты_поиска.append({
                        'id': офицер['id'],
                        'отображение': отображение,
                        'фамилия': офицер['фамилия'],
                        'имя': офицер['имя'],
                        'отчество': офицер['отчество'],
                        'звание': звание,
                        'должность': должность
                    })
                
                # Устанавливаем значения для комбобокса
                self.combobox['values'] = values
                
                # Открываем выпадающий список
                self.combobox.event_generate('<Down>')
            else:
                # Если результатов нет, очищаем список значений
                self.combobox['values'] = []
                
        except Exception as e:
            logger.error(f"Ошибка при поиске офицеров: {e}")
            # Очищаем список значений
            self.combobox['values'] = []
    
    def _on_item_selected(self, event):
        """Обработчик выбора офицера из выпадающего списка"""
        текст = self.combobox.get().strip()
        
        for офицер in self.результаты_поиска:
            if офицер['отображение'] == текст:
                # Вызываем функцию обратного вызова, если она задана
                if self.callback:
                    self.callback(офицер)
                break
    
    def получить_выбранного_офицера(self):
        """Возвращает данные выбранного офицера или None, если офицер не выбран"""
        текст = self.combobox.get().strip()
        
        # Если текст пустой или равен placeholder, возвращаем None
        if not текст or текст == self.placeholder:
            return None
        
        # Ищем офицера в результатах поиска
        for офицер in self.результаты_поиска:
            if офицер['отображение'] == текст:
                return офицер
        
        return None
    
    def очистить(self):
        """Очищает поле поиска"""
        self.combobox.set(self.placeholder)
        self.combobox.config(foreground='gray')
        self.combobox['values'] = []
        self.результаты_поиска = []
    
    def установить_значение(self, офицер):
        """Устанавливает значение в поле поиска"""
        if офицер:
            self.combobox.set(офицер['отображение'])
            self.combobox.config(foreground='black')
            
            # Добавляем офицера в результаты поиска
            if офицер not in self.результаты_поиска:
                self.результаты_поиска.append(офицер)