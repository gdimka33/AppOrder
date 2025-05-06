import tkinter as tk
from tkinter import ttk
from БД_соединение import выполнить_запрос
from logger import logger

class ПоискОфицера(ttk.Frame):
    """
    Виджет для поиска офицеров.
    Состоит из поля ввода и выпадающего списка результатов.
    """
    def __init__(self, родитель, callback=None, placeholder="Введите фамилию офицера для поиска...", высота_списка=5):
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
        self.entry.bind("<Return>", self._on_return)
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
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Создаем список с плоским стилем и рамкой
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
                              highlightbackground='#ADD8E6',
                              highlightcolor='#ADD8E6')
        self.список.pack(fill="both", expand=True)
        
        # Привязываем события
        # self.список.bind("<Enter>", lambda e: self.entry.focus_set()) # Убрал, чтобы фокус не перескакивал
        self.список.bind("<Motion>", self._on_mouse_motion)
        self.список.bind("<Button-1>", self._on_click_item)
        self.popup.bind("<FocusOut>", self._on_popup_focus_out)

    def _выполнить_поиск(self, текст_поиска):
        """Выполняет поиск офицеров"""
        try:
            запрос = """
                SELECT о.id, о.фамилия, о.имя, о.отчество, 
                       з.наименование as звание, 
                       д.наименование as должность,
                       п.наименование as подразделение
                FROM офицеры о
                LEFT JOIN звания з ON о.звание_id = з.id
                LEFT JOIN должности д ON о.должность_id = д.id
                LEFT JOIN подразделения п ON о.подразделение_id = п.id
                WHERE LOWER(о.фамилия) LIKE LOWER(?) 
                   OR LOWER(о.имя) LIKE LOWER(?) 
                   OR LOWER(о.отчество) LIKE LOWER(?)
                ORDER BY о.фамилия, о.имя
            """
            параметры = (f"%{текст_поиска}%", f"%{текст_поиска}%", f"%{текст_поиска}%")
            результат = выполнить_запрос(запрос, параметры)
            
            self.результаты_поиска = []
            if результат:
                if not self.popup or not self.список:
                    self._создать_список()
                self.список.delete(0, tk.END)
                
                for офицер in результат:
                    # Преобразуем первые буквы в заглавные
                    фамилия = офицер['фамилия'].capitalize()
                    имя = офицер['имя'].capitalize()
                    отчество = офицер['отчество'].capitalize() if офицер['отчество'] else ''
                    
                    # Форматируем ФИО
                    фио = f"{фамилия} {имя[0]}.{отчество[0]}." if отчество else f"{фамилия} {имя[0]}."
                    
                    # Добавляем звание, должность и подразделение
                    звание = офицер['звание'].capitalize() if офицер['звание'] else ''
                    должность = офицер['должность'].capitalize() if офицер['должность'] else ''
                    подразделение = офицер['подразделение'] if офицер['подразделение'] else ''
                    
                    отображение = f"{звание} {фио} - {должность}"
                    if подразделение:
                        отображение += f" ({подразделение})"
                    
                    self.список.insert(tk.END, отображение)
                    self.результаты_поиска.append({
                        'id': офицер['id'],
                        'отображение': отображение,
                        'фамилия': фамилия,
                        'имя': имя,
                        'отчество': отчество,
                        'звание': звание,
                        'должность': должность,
                        'подразделение': подразделение
                    })
                self._показать_список()
            else:
                self._скрыть_список()
                    
        except Exception as e:
            logger.error(f"Ошибка при поиске офицеров: {e}")
            self._скрыть_список()

    def _показать_список(self):
        """Показывает выпадающий список"""
        if self.popup and self.список.size() > 0:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height()
            width = self.entry.winfo_width() # Получаем ширину поля ввода
            # Устанавливаем геометрию с учетом ширины
            self.popup.geometry(f"{width}x{self.список.winfo_reqheight()}+{x}+{y}") 
            self.popup.deiconify()
            self.popup.lift()
            # self.popup.focus_set() # Убрал фокус с попапа, чтобы ввод не прерывался

    def _скрыть_список(self, event=None):
        """Скрывает выпадающий список"""
        if self.popup:
            self.popup.withdraw()

    def _on_mouse_motion(self, event):
        """Обработчик движения мыши над списком"""
        self.список.selection_clear(0, tk.END)
        self.список.selection_set(self.список.nearest(event.y))

    def _on_click_item(self, event):
        """Обработчик клика по элементу списка"""
        self._выбрать_элемент()

    def _выбрать_элемент(self):
        """Выбирает элемент из списка"""
        индекс = self.список.curselection()
        if индекс:
            текст = self.список.get(индекс)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, текст)
            self.entry.config(foreground='black')
            self._скрыть_список()
            for офицер in self.результаты_поиска:
                if офицер['отображение'] == текст:
                    if self.callback:
                        self.callback(офицер)
                    break

    def _on_popup_focus_out(self, event):
        """Обработчик потери фокуса выпадающим окном"""
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
        """Обработчик ввода текста в поле поиска"""
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
            return
        
        # Отменяем предыдущий таймер, если он есть
        if self.search_timer:
            self.after_cancel(self.search_timer)
            
        текст_поиска = self.entry.get().strip()
        if текст_поиска and текст_поиска != self.placeholder:
            # Запускаем поиск с задержкой в 300 мс
            self.search_timer = self.after(300, lambda: self._выполнить_поиск(текст_поиска))
        else:
            self._скрыть_список()

    def _on_return(self, event):
        """Обработчик нажатия Enter"""
        self._выбрать_элемент()

    def получить_выбранного_офицера(self):
        """Возвращает данные выбранного офицера или None, если офицер не выбран"""
        текст = self.entry.get().strip()
        if not текст or текст == self.placeholder:
            return None
        for офицер in self.результаты_поиска:
            if офицер['отображение'] == текст:
                return офицер
        return None

    def очистить(self):
        """Очищает поле поиска"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(foreground='gray')
        self._скрыть_список()
        self.результаты_поиска = []

    def установить_значение(self, офицер):
        """Устанавливает значение в поле поиска"""
        if офицер:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, офицер['отображение'])
            self.entry.config(foreground='black')
            if офицер not in self.результаты_поиска:
                self.результаты_поиска.append(офицер)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Поиск офицера")
    root.geometry("400x200")
    
    def on_select(офицер):
        print(f"Выбран офицер: {офицер['отображение']}")
    
    поиск = ПоискОфицера(root, callback=on_select)
    поиск.pack(pady=20)
    
    root.mainloop()