import tkinter as tk
from tkinter import ttk
from БД_соединение import выполнить_запрос
from logger import logger
import datetime

class ПоискКурсанта(ttk.Frame):
    """
    Виджет для поиска курсантов.
    Состоит из поля ввода и выпадающего списка результатов.
    """
    def __init__(self, родитель, callback=None, placeholder="Введите фамилию Курсанта для поиска...", высота_списка=5):
        super().__init__(родитель)
        
        self.callback = callback
        self.placeholder = placeholder
        self.результаты_поиска = []
        self.высота_списка = высота_списка
        self.root = родитель
        self.search_timer = None  # Таймер для задержки поиска
        
        # Создаем контейнер
        self.pack(fill='x', expand=True)
        
        # Создаем поле ввода
        self.entry = ttk.Entry(self)
        self.entry.pack(fill='x', padx=5, pady=5)
        self.entry.insert(0, self.placeholder)
        self.entry.config(foreground='gray')
        
        # Создаем выпадающее окно
        self.popup = None
        self.список = None
        
        # Привязываем обработчики событий
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Return>", self._on_return)  # Изменено с _on_enter на _on_return
        self.entry.bind("<Escape>", self._скрыть_список)
        
    def _создать_список(self):
        """Создает выпадающий список"""
        if self.popup:
            self.popup.destroy()
            
        self.popup = tk.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.transient()
        
        # Создаем рамку
        frame = ttk.Frame(self.popup)
        frame.pack(fill="both", expand=True, padx=1, pady=1)  # Добавляем отступы для рамки
        
        # Создаем список с плоским стилем
        self.список = tk.Listbox(frame, 
                              height=self.высота_списка,
                              activestyle='none',
                              selectmode="single",
                              relief='flat',
                              borderwidth=0,
                              highlightthickness=1,
                              background='white',
                              selectbackground='#E8E8E8',
                              selectforeground='black',
                              highlightbackground='#ADD8E6',  # Светло-голубая рамка
                              highlightcolor='#ADD8E6')
        self.список.pack(fill="both", expand=True)
        
        # Привязываем события
        # self.список.bind("<Enter>", lambda e: self.entry.focus_set()) # Убрал, чтобы фокус не перескакивал
        self.список.bind("<Motion>", self._on_mouse_motion)
        self.список.bind("<Button-1>", self._on_click_item)
        self.popup.bind("<FocusOut>", self._on_popup_focus_out)
        
    def _показать_список(self):
        """Показывает выпадающий список"""
        if not self.popup:
            self._создать_список()
            
        # Позиционируем список под полем ввода
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()
        
        self.popup.geometry(f"{width}x{self.список.winfo_reqheight()}+{x}+{y}")
        self.popup.deiconify()
        # self.entry.focus_set() # Убрал фокус с поля ввода, чтобы он не перехватывался у списка
        
    def _скрыть_список(self, event=None):
        """Скрывает выпадающий список"""
        if self.popup:
            self.popup.withdraw()

    def _on_mouse_motion(self, event):
        """Обработчик движения мыши над списком"""
        index = self.список.nearest(event.y)
        self.список.selection_clear(0, tk.END)
        self.список.selection_set(index)

    def _on_click_item(self, event):
        """Обработчик клика по элементу списка"""
        if self.список.curselection():
            индекс = self.список.curselection()[0]
            self._выбрать_элемент(индекс)

    def _выбрать_элемент(self, индекс):
        """Выбирает элемент из списка"""
        if 0 <= индекс < len(self.результаты_поиска):
            курсант = self.результаты_поиска[индекс]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, курсант['отображение'])
            self.entry.config(foreground='black')
            self._скрыть_список()
            if self.callback:
                self.callback(курсант)

    def _on_popup_focus_out(self, event):
        """Обработчик потери фокуса выпадающим списком"""
        # Скрываем список, только если фокус ушел не на поле ввода
        if self.focus_get() != self.entry:
            self._скрыть_список()

    def _on_focus_in(self, event):
        """Обработчик получения фокуса полем ввода"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='black')
            
    def _on_focus_out(self, event):
        """Обработчик потери фокуса полем ввода"""
        # Используем after для небольшой задержки, чтобы проверить, куда ушел фокус
        self.after(100, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        """Проверяет фокус и скрывает список, если фокус не на списке или поле ввода"""
        focused_widget = self.focus_get()
        # Не скрываем, если фокус на списке или его дочерних элементах, или на самом поле ввода
        if focused_widget != self.entry and (not self.popup or focused_widget != self.список):
            if not self.entry.get():
                self.entry.insert(0, self.placeholder)
                self.entry.config(foreground='gray')
            self._скрыть_список()
        elif not self.entry.get() and focused_widget != self.entry:
             # Если поле пустое и фокус не на нем, но на списке - ставим плейсхолдер
             # Это предотвращает исчезновение плейсхолдера при клике на список
             # Но не скрываем список
             self.entry.insert(0, self.placeholder)
             self.entry.config(foreground='gray')
            
    def _on_key_release(self, event):
        """Обработчик ввода текста"""
        # Игнорируем только управляющие клавиши
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Shift_L', 'Shift_R', 
                           'Control_L', 'Control_R', 'Caps_Lock'):
            return
            
        # Отменяем предыдущий таймер, если он есть
        if self.search_timer:
            self.after_cancel(self.search_timer)
            
        текст = self.entry.get().strip()
        if текст and текст != self.placeholder:
            # Запускаем поиск с задержкой в 300 мс
            # Приводим текст к нижнему регистру для поиска
            self.search_timer = self.after(300, lambda t=текст.lower(): self._выполнить_поиск(t))
        else:
            self._скрыть_список()
            
    def _выполнить_поиск(self, текст_поиска):
        """Выполняет поиск курсантов"""
        try:
            запрос = """
                SELECT 
                    к.id, 
                    к.фамилия, 
                    к.имя, 
                    к.отчество,
                    к.год_набора,
                    з.наименование as звание
                FROM курсанты к
                LEFT JOIN звания з ON к.звание_id = з.id
                WHERE LOWER(к.фамилия) LIKE LOWER(?) 
                   OR LOWER(к.имя) LIKE LOWER(?) 
                   OR LOWER(к.отчество) LIKE LOWER(?)
                ORDER BY к.фамилия, к.имя
            """
            # Добавляем % к тексту поиска
            текст_поиска = f"%{текст_поиска}%"
            параметры = (текст_поиска, текст_поиска, текст_поиска)
            результат = выполнить_запрос(запрос, параметры)
            
            self.результаты_поиска = []
            if результат:
                if not self.popup or not self.список:
                    self._создать_список()
                self.список.delete(0, tk.END)
                
                текущий_год = datetime.datetime.now().year
                
                for курсант in результат:
                    # Преобразуем первые буквы в заглавные
                    фамилия = курсант['фамилия'].capitalize()
                    имя = курсант['имя'].capitalize()
                    отчество = курсант['отчество'].capitalize() if курсант['отчество'] else ''
                    
                    # Рассчитываем курс
                    курс = текущий_год - курсант['год_набора'] + 1
                    if курс < 1: курс = 1
                    if курс > 5: курс = 5
                    
                    # Форматируем ФИО
                    фио = f"{фамилия} {имя[0]}.{отчество[0]}." if отчество else f"{фамилия} {имя[0]}."
                    
                    # Добавляем звание и курс
                    звание = курсант['звание'].capitalize() if курсант['звание'] else ''
                    отображение = f"{фио} - {звание}, {курс} курс"
                    
                    self.список.insert(tk.END, отображение)
                    self.результаты_поиска.append({
                        'id': курсант['id'],
                        'отображение': отображение,
                        'фамилия': фамилия,
                        'имя': имя,
                        'отчество': отчество,
                        'звание': звание,
                        'курс': курс,
                        'год_набора': курсант['год_набора']
                    })
                self._показать_список()
            else:
                self._скрыть_список()
                    
        except Exception as e:
            logger.error(f"Ошибка при поиске курсантов: {e}")
            self._скрыть_список()

    def _on_select(self, event):
        """Обработчик выбора из списка"""
        selection = self.список.curselection()
        if selection:
            индекс = selection[0]

    def _on_return(self, event=None):
        """Обработчик нажатия Enter"""
        if self.popup and self.popup.winfo_ismapped():
            if self.список.curselection():
                индекс = self.список.curselection()[0]
                self._выбрать_элемент(индекс)
            else:
                # Если ничего не выбрано, но есть результаты, выбираем первый
                if self.результаты_поиска:
                    self._выбрать_элемент(0)
        return "break"  # Предотвращаем дальнейшую обработку события

    def получить_выбранного_курсанта(self):
        """Возвращает выбранного курсанта"""
        текст = self.entry.get().strip()
        if not текст or текст == self.placeholder:
            return None
        return next((к for к in self.результаты_поиска if к['отображение'] == текст), None)

    def очистить(self):
        """Очищает поле поиска"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(foreground='gray')
        self._скрыть_список()
        self.результаты_поиска = []

    def установить_значение(self, курсант):
        """Устанавливает значение в поле поиска"""
        if not курсант or not isinstance(курсант, dict):
            return False
            
        required_keys = ['id', 'фамилия', 'имя', 'отчество']
        if not all(key in курсант for key in required_keys):
            return False
            
        # Формируем отображаемое значение
        фио = f"{курсант['фамилия']} {курсант['имя'][0]}.{курсант['отчество'][0] if курсант['отчество'] else ''}"
        курсант['отображение'] = фио
            
        self.entry.delete(0, tk.END)
        self.entry.insert(0, фио)
        self.entry.config(foreground='black')
            
        # Добавляем курсанта в результаты поиска
        if курсант not in self.результаты_поиска:
            self.результаты_поиска.append(курсант)
        
        return True

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Поиск курсантов")
    root.geometry("300x200")

    поиск = ПоискКурсанта(root, callback=lambda курсант: print(курсант))
    поиск.pack(pady=20)

    root.mainloop()