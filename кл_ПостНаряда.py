import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Literal
from БД_соединение import выполнить_запрос
from logger import logger
from ви_ПоискОфицера import ПоискОфицера
from ви_ПоискКурсанта import ПоискКурсанта

class ПостНаряда(ttk.Frame):
    def __init__(
        self,
        master,
        пост_ид: int,  # Добавляем ID поста из БД
        дата_наряда: datetime,
        подразделение: str,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.пост_ид = пост_ид
        self.дата_наряда = дата_наряда
        self.подразделение = подразделение
        
        # Загружаем данные поста из БД
        self.данные_поста = self._загрузить_данные_поста()
        
        # Переменные состояния
        self.is_assigned_var = tk.BooleanVar(value=True)
        self.has_officer_var = tk.BooleanVar(value=True)  # Всегда True
        self.has_personnel_var = tk.BooleanVar(value=True)  # Всегда True
        # По умолчанию устанавливаем officer для всех постов
        self.officer_type_var = tk.StringVar(value="officer")
        self.officer_name_var = tk.StringVar(value="")
        # Изменяем начальное значение количества дневальных
        self.personnel_count_var = tk.IntVar(value=self.данные_поста['дневальный_кол'])
        self.max_personnel = self.данные_поста['дневальный_кол']
        self.personnel_names_vars = [tk.StringVar(value="") for _ in range(max(1, self.данные_поста['дневальный_кол']))]
        
        # Создание виджетов
        self._create_widgets()
        self._setup_bindings()
        self._update_widgets_state()

    def _загрузить_данные_поста(self) -> dict:
        """Загружает данные поста из БД"""
        try:
            запрос = """
                SELECT 
                    id,
                    наименование,
                    дежурный,
                    дежурный_кол,
                    дежурный_офицер,
                    дежурный_курсант,
                    дневальный,
                    дневальный_кол
                FROM посты 
                WHERE id = ?
            """
            результат = выполнить_запрос(запрос, (self.пост_ид,))
            if результат:
                # Создаем словарь с фиксированными ключами
                поля = [
                    'id', 
                    'наименование', 
                    'дежурный', 
                    'дежурный_кол',
                    'дежурный_офицер',
                    'дежурный_курсант',
                    'дневальный',
                    'дневальный_кол'
                ]
                данные = dict(zip(поля, результат[0]))
                
                # Проверяем наличие всех необходимых ключей
                обязательные_поля = {
                    'id': self.пост_ид,
                    'наименование': 'Неизвестный пост',
                    'дежурный': False,
                    'дежурный_кол': 0,
                    'дежурный_офицер': False,
                    'дежурный_курсант': False,
                    'дневальный': False,
                    'дневальный_кол': 0
                }
                
                # Заполняем отсутствующие поля значениями по умолчанию
                for поле, значение_по_умолчанию in обязательные_поля.items():
                    if поле not in данные or данные[поле] is None:  # заменили "или" на "or"
                        данные[поле] = значение_по_умолчанию
                        logger.warning(f"Поле {поле} отсутствует в данных поста {self.пост_ид}, установлено значение по умолчанию")
                
                # Преобразуем булевы значения
                for поле in ['дежурный', 'дежурный_офицер', 'дежурный_курсант', 'дневальный']:
                    данные[поле] = bool(данные[поле])
                
                # Преобразуем числовые значения
                for поле in ['дежурный_кол', 'дневальный_кол']:
                    данные[поле] = int(данные[поле])
                
                return данные
            else:
                raise ValueError(f"Пост с ID {self.пост_ид} не найден")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных поста {self.пост_ид}: {e}")
            return {
                'id': self.пост_ид,
                'наименование': 'Неизвестный пост',
                'дежурный': False,
                'дежурный_кол': 0,
                'дежурный_офицер': False,
                'дежурный_курсант': False,
                'дневальный': False,
                'дневальный_кол': 0
            }

    def _create_widgets(self):
        """Создает все элементы интерфейса в зависимости от данных поста"""
        self.configure(borderwidth=1, relief="solid", padding=5)
        
        # Создаем главный контейнер
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="x")
        
        # Фрейм для чекбокса (первая колонка)
        self.checkbox_frame = ttk.Frame(self.main_container, width=30)
        self.checkbox_frame.pack(side="left", anchor="n")
        
        self.status_check = ttk.Checkbutton(
            self.checkbox_frame, 
            variable=self.is_assigned_var
        )
        self.status_check.pack(padx=5, pady=5)
        
        # Фрейм для названия наряда (вторая колонка)
        self.name_frame = ttk.Frame(self.main_container)
        self.name_frame.pack(side="left", fill="y", padx=5)
        
        self.name_label = ttk.Label(
            self.name_frame,
            text=self.данные_поста['наименование'],
            font=('Helvetica', 10, 'bold'),
            width=30,  # Фиксированная ширина в символах
            wraplength=250,  # Максимальная ширина текста в пикселях для переноса
            justify="left"
        )
        self.name_label.pack(anchor="w", pady=5)
        
        # Фрейм для дежурных/дневальных (третья колонка)
        self.duty_frame = ttk.Frame(self.main_container)
        self.duty_frame.pack(side="left", fill="x", expand=True)

        # Разделяем на две части
        self.duty_labels_frame = ttk.Frame(self.duty_frame)
        self.duty_labels_frame.pack(side="left", padx=(5, 10), fill="y")
        
        self.duty_entries_frame = ttk.Frame(self.duty_frame)
        self.duty_entries_frame.pack(side="left", fill="both", expand=True)
        
        # Создаем элементы управления
        if self.данные_поста['дежурный']:
            self._create_officer_widgets()
        
        if self.данные_поста['дневальный']:
            self._create_personnel_widgets()
            
        # Фрейм для даты (четвертая колонка)
        self.time_frame = ttk.Frame(self.main_container, width=50)
        self.time_frame.pack(side="left", fill="y")
        self.time_frame.pack_propagate(False)
        
        self.time_label = ttk.Label(
            self.time_frame,
            text=self.дата_наряда.strftime("%d.%m.%Y\n%H:%M"),
            justify="left"
        )
        self.time_label.pack(anchor="ne", padx=5, pady=5)

    def _create_officer_widgets(self):
        """Создает виджеты для дежурного"""
        # Метка "Дежурный" в левой части только если есть дневальные
        if self.данные_поста['дневальный']:
            ttk.Label(self.duty_labels_frame, text="Дежурный").pack(anchor="nw", pady=(0, 5))
        
        # Очищаем фрейм для ввода
        for widget in self.duty_entries_frame.winfo_children():
            widget.destroy()
        
        # Создаем фрейм для радиокнопок
        type_frame = ttk.Frame(self.duty_entries_frame)
        type_frame.pack(fill="x", pady=(0, 5))
        
        # Показываем радиокнопки только если разрешены оба типа дежурных
        if self.данные_поста['дежурный_офицер'] and self.данные_поста['дежурный_курсант']:
            ttk.Radiobutton(
                type_frame,
                text="Офицер",
                variable=self.officer_type_var,
                value="officer",
                command=self._update_officer_entry
            ).pack(side="left", padx=5)
            
            ttk.Radiobutton(
                type_frame,
                text="Курсант",
                variable=self.officer_type_var,
                value="cadet",
                command=self._update_officer_entry
            ).pack(side="left", padx=5)
        elif self.данные_поста['дежурный_офицер']:
            self.officer_type_var.set("officer")
        elif self.данные_поста['дежурный_курсант']:
            self.officer_type_var.set("cadet")
        
        # Создаем виджет поиска
        self._update_officer_entry()

    def _update_officer_entry(self):
        """Обновляет поле поиска в зависимости от выбранного типа дежурного"""
        # Удаляем существующий виджет поиска
        for widget in self.duty_entries_frame.winfo_children():
            if isinstance(widget, (ПоискОфицера, ПоискКурсанта)):
                widget.destroy()
        
        # Создаем новый виджет поиска
        search_frame = ttk.Frame(self.duty_entries_frame)
        search_frame.pack(fill="x", expand=True)
        
        if self.officer_type_var.get() == "officer":
            self.officer_search = ПоискОфицера(
                search_frame,
                callback=self._on_officer_selected
            )
        else:
            self.officer_search = ПоискКурсанта(
                search_frame,
                callback=self._on_officer_selected
            )
        self.officer_search.pack(fill="x", expand=True)

    def _create_personnel_widgets(self):
        """Создает виджеты для дневальных"""
        # Левая часть - заголовок
        personnel_label_frame = ttk.Frame(self.duty_labels_frame)
        personnel_label_frame.pack(anchor="nw", fill="x")
        
        # Заголовок
        header_text = "Дневальные" if self.данные_поста['дневальный_кол'] > 1 else "Дневальный"
        ttk.Label(personnel_label_frame, text=header_text).pack(anchor="nw")
        
        # Контроль количества
        if self.данные_поста['дневальный_кол'] > 1:
            count_frame = ttk.Frame(personnel_label_frame)
            count_frame.pack(anchor="nw", pady=2)
            
            ttk.Button(count_frame, text="-", width=2,
                      command=lambda: self._change_personnel_count(-1)).pack(side="left")
            ttk.Label(count_frame, textvariable=self.personnel_count_var,
                     width=3, anchor="center").pack(side="left", padx=2)
            ttk.Button(count_frame, text="+", width=2,
                      command=lambda: self._change_personnel_count(1)).pack(side="left")
        
        # Правая часть - поля поиска для дневальных
        self.personnel_entries_frame = ttk.Frame(self.duty_entries_frame)
        self.personnel_entries_frame.pack(fill="x")
        
        # Создаем поля поиска
        self._update_personnel_entries()

    def _setup_bindings(self):
        """Настраивает привязки событий"""
        self.is_assigned_var.trace_add("write", lambda *_: self._update_widgets_state())
        self.has_officer_var.trace_add("write", lambda *_: self._update_widgets_state())
        self.has_personnel_var.trace_add("write", lambda *_: self._update_widgets_state())
        self.personnel_count_var.trace_add("write", lambda *_: self._update_personnel_count())
    
    def _update_widgets_state(self):
        """Обновляет состояние виджетов"""
        # Состояние активности
        active = self.is_assigned_var.get()
        
        # Список базовых виджетов
        base_widgets = [
            'name_label',
            'entry_frame',
            'time_frame'
        ]
        
        # Обновляем состояние базовых виджетов
        for widget_name in base_widgets:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                if hasattr(widget, 'state'):
                    widget.state(["!disabled" if active else "disabled"])
        
        # Обновляем состояние виджетов дежурного
        if self.данные_поста['дежурный']:
            if hasattr(self, 'officer_entry'):
                self.officer_entry.state(["!disabled" if active else "disabled"])
                
            if hasattr(self, 'officer_type_frame'):
                self.officer_type_frame.state(["!disabled" if active else "disabled"])
        
        # Обновляем состояние виджетов дневальных
        if self.данные_поста['дневальный']:
            if hasattr(self, 'personnel_control_frame'):
                self.personnel_control_frame.state(["!disabled" if active else "disabled"])
                
            if hasattr(self, 'personnel_entries_frame'):
                for entry in self.personnel_entries_frame.winfo_children():
                    if hasattr(entry, 'state'):
                        entry.state(["!disabled" if active else "disabled"])
        
        # Обновляем цвет неактивных полей
        self._update_disabled_style()
    
    def _update_disabled_style(self):
        """Обновляет стиль неактивных полей"""
        style = ttk.Style()
        style.configure("Disabled.TEntry", foreground="gray")
        style.configure("Normal.TEntry", foreground="black")
        
        # Поле дежурного
        if hasattr(self, 'officer_entry'):
            if self.officer_entry.instate(["disabled"]):
                self.officer_entry.configure(style="Disabled.TEntry")
            else:
                self.officer_entry.configure(style="Normal.TEntry")
        
        # Поля дневальных
        if hasattr(self, 'personnel_entries_frame'):
            for entry in self.personnel_entries_frame.winfo_children():
                if entry.instate(["disabled"]):
                    entry.configure(style="Disabled.TEntry")
                else:
                    entry.configure(style="Normal.TEntry")
    
    def _update_personnel_entries(self):
        """Обновляет поля поиска дневальных"""
        # Очищаем существующие поля
        for widget in self.personnel_entries_frame.winfo_children():
            widget.destroy()
        
        # Определяем количество полей
        count = self.personnel_count_var.get()
        
        # Создаем поля поиска
        self.personnel_searches = []
        for i in range(count):
            search_frame = ttk.Frame(self.personnel_entries_frame)
            search_frame.pack(fill="x", pady=(0, 2))
            
            search = ПоискКурсанта(
                search_frame,
                callback=lambda idx=i: self._on_personnel_selected(idx)
            )
            search.pack(fill="x", expand=True)
            self.personnel_searches.append(search)
    
    def _change_personnel_count(self, delta):
        """Изменяет количество дневальных в пределах допустимого диапазона"""
        new_count = self.personnel_count_var.get() + delta
        if 1 <= new_count <= self.max_personnel:
            self.personnel_count_var.set(new_count)
    
    def _update_personnel_count(self, *args):
        """Обновляет поля при изменении количества дневальных"""
        self._update_personnel_entries()
    
    def сохранить_наряд(self):
        """Сохраняет данные наряда в БД"""
        try:
            данные = self.get_data()
            запрос = """
                INSERT INTO наряды (
                    пост_ид,
                    дата_наряда,
                    подразделение,
                    дежурный_офицер,
                    дежурный_фио,
                    количество_дневальных,
                    дневальные_список
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            параметры = (
                self.пост_ид,
                self.дата_наряда.strftime("%Y-%m-%d %H:%M:%S"),
                self.подразделение,
                1 if данные['officer_type'] == 'officer' else 0,
                данные['officer_name'],
                данные['personnel_count'],
                ','.join(данные['personnel_names'])
            )
            выполнить_запрос(запрос, параметры)
            logger.info(f"Наряд для поста {self.пост_ид} успешно сохранен")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении наряда для поста {self.пост_ид}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить наряд: {e}")
            return False

    def get_data(self):
        """Возвращает данные из виджета"""
        return {
            "пост_ид": self.пост_ид,
            "наименование": self.данные_поста['наименование'],
            "дата_наряда": self.дата_наряда,
            "подразделение": self.подразделение,
            "is_assigned": self.is_assigned_var.get(),
            "has_officer": self.has_officer_var.get(),
            "officer_type": self.officer_type_var.get(),
            "officer_name": self.officer_name_var.get(),
            "has_personnel": self.has_personnel_var.get(),
            "personnel_count": self.personnel_count_var.get(),
            "personnel_names": [var.get() for var in self.personnel_names_vars[:self.personnel_count_var.get()]]
        }

    def _on_officer_selected(self, officer):
        """Обработчик выбора офицера"""
        if officer:
            self.officer_name_var.set(officer['отображение'])
    
    def _on_officer_type_changed(self, *args):
        """Обработчик изменения типа дежурного"""
        self._update_officer_entry()
        self.officer_name_var.set("")  # Очищаем поле при смене типа


# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Улучшенный виджет наряда")
    
    # Создаем стиль для виджета
    style = ttk.Style()
    style.configure("Duty.TFrame", borderwidth=1, relief="solid")
    
    # Создаем тестовый наряд
    duty = ПостНаряда(
        root,
        пост_ид=1,
        дата_наряда=datetime(2023, 12, 15, 8, 0),
        подразделение="1-я рота",
        style="Duty.TFrame"
    )
    duty.pack(fill="x", padx=10, pady=5, ipady=5)
    
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Пост Наряда")
    
    # Пример создания виджета
    пост_наряда = ПостНаряда(root, 1, datetime.now(), "1-я рота")
    пост_наряда.pack(padx=10, pady=10)
    
    root.mainloop()