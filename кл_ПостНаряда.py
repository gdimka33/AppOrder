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
        пост_ид: int,
        дата_наряда: datetime,
        подразделение: str,
        **kwargs
    ):
        # Initialize instance variables first
        self.пост_ид = пост_ид
        self.дата_наряда = дата_наряда
        self.подразделение = подразделение
        
        # Создаем стиль для неактивных элементов
        style = ttk.Style()
        style.configure('Dim.TRadiobutton', foreground='#666666')
        
        # Initialize other variables
        self.is_assigned_var = tk.BooleanVar(value=True)
        self.тип_сотрудника_var = tk.StringVar(value="officer")  # Set default here ONLY
        self.количество_дневальных_var = tk.IntVar() # Variable for dnavalny quantity
        self.поля_ввода_дневальные = [] # List to hold dnavalny input fields
        
        # Load post data
        self.данные_поста = self._загрузить_данные_поста()
        
        # Initialize instance
        super().__init__(master, **kwargs)
        
        # Configure frame with minimum height and full width (no vertical expansion)
        self.pack(fill='x')  # Only fill horizontally
        self.configure(height=50)  # Set fixed minimum height to 50 pixels
        
        # Создаем фрейм для чекбокса
        self.фрейм_назначен = ttk.Frame(self)
        self.фрейм_назначен.pack(side='left', anchor='n') # Выравнивание по верхнему краю
        
        # Чекбокс
        self.status_check = ttk.Checkbutton(
            self.фрейм_назначен, 
            variable=self.is_assigned_var,
            command=self._обновить_состояние_элементов_в_зависимости_от_назначения # Добавляем команду
        )
        self.status_check.pack()

        # Создаем фрейм для наименования и даты
        self.фрейм_для_наименование_дата = ttk.Frame(self)
        self.фрейм_для_наименование_дата.pack(side='top', fill='x')
        
        # Фрейм для наименования поста
        self.фрейм_наименование = ttk.Frame(self.фрейм_для_наименование_дата)
        self.фрейм_наименование.pack(side='left', fill='x', expand=True)
        
        # Метка с наименованием поста
        self.name_label = ttk.Label(
            self.фрейм_наименование,
            text=self.данные_поста['наименование'],
            font=('Helvetica', 10, 'bold'),
            justify='left'  # Add this line to align text to the left
        )
        self.name_label.pack(anchor='w')  # Add anchor='w' for left alignment
        
        # Фрейм для даты
        self.фрейм_дата = ttk.Frame(self.фрейм_для_наименование_дата)
        self.фрейм_дата.pack(side='left')
        
        # Метка с датой
        self.date_label = ttk.Label(
            self.фрейм_дата,
            text=self.дата_наряда.strftime("%d.%m.%Y"),
            font=('Helvetica', 10)
        )
        self.date_label.pack()

        # Создаем основной фрейм для полей ввода
        self.фрейм_поля_ввода = ttk.Frame(self)
        self.фрейм_поля_ввода.pack(side='left', fill='both', expand=True)
        
        # Создаем фрейм для выбора типа сотрудника
        self.фрейм_выбор_типа_сотрудника = ttk.Frame(self.фрейм_поля_ввода)
        # Не пакуем фрейм сразу, сделаем это после добавления кнопок

        # Определяем доступные типы
        can_assign_officer = self.данные_поста.get('дежурный_офицер', False)
        can_assign_cadet = self.данные_поста.get('дежурный_курсант', False)

        # Логика отображения выбора типа и установки значения по умолчанию
        if can_assign_officer and can_assign_cadet:
            # Оба типа доступны - показываем выбор
            self.тип_сотрудника_var.set("officer") # По умолчанию офицер
            ttk.Radiobutton(
                self.фрейм_выбор_типа_сотрудника,
                text="Офицер",
                variable=self.тип_сотрудника_var,
                value="officer",
                command=self._обновить_поле_ввода_дежурный
            ).pack(side='top', anchor='w') # Изменено side на 'top' и добавлен anchor='w', pady=2
            ttk.Radiobutton(
                self.фрейм_выбор_типа_сотрудника,
                text="Курсант",
                variable=self.тип_сотрудника_var,
                value="cadet",
                command=self._обновить_поле_ввода_дежурный
            ).pack(side='top', anchor='w') # Изменено side на 'top' и добавлен anchor='w', pady=2
            self.фрейм_выбор_типа_сотрудника.pack(side='left', fill='y') # Изменено fill на 'y' и padx
        elif can_assign_officer:
            # Только офицер доступен - скрываем выбор, устанавливаем офицера
            self.тип_сотрудника_var.set("officer")
            # Фрейм self.фрейм_выбор_типа_сотрудника не пакуется
        elif can_assign_cadet:
            # Только курсант доступен - скрываем выбор, устанавливаем курсанта
            self.тип_сотрудника_var.set("cadet")
            # Фрейм self.фрейм_выбор_типа_сотрудника не пакуется
        else:
            # Ни один тип не доступен
            self.тип_сотрудника_var.set("")
            # Фрейм self.фрейм_выбор_типа_сотрудника не пакуется

        # Remove duplicate default setting and trace_add
        # self.тип_сотрудника_var.set("officer")  # No longer needed
        # self.тип_сотрудника_var.trace_add('write', lambda *_: self._обновить_поле_ввода_дежурный()) # No longer needed
        
        # Создаем фрейм для полей ввода
        self.фрейм_поля_для_ввода = ttk.Frame(self.фрейм_поля_ввода)
        self.фрейм_поля_для_ввода.pack(side='right', fill='both', expand=True)

        # Создаем фрейм для дежурных
        self.фрейм_дежурный = ttk.Frame(self.фрейм_поля_для_ввода)
        self.фрейм_дежурный.pack(side='top', fill='both', expand=True)
        
        # Лейбл "Дежурный" (отображается, если можно назначить курсанта или обоих)
        if not can_assign_officer or can_assign_cadet:
            self.лейбл_дежурный = ttk.Label(self.фрейм_дежурный, text="Дежурный")
            # ширина 15
            self.лейбл_дежурный.configure(width=15)  # Set width to 15 characters
            self.лейбл_дежурный.pack(side='left', anchor='n') # Выравнивание по верхнему краю
        else:
            self.лейбл_дежурный = None # Убедимся, что атрибут существует, даже если метка не создана
        
        # Поле ввода (будет обновляться в зависимости от выбора)
        self.поле_ввода_дежурный = None
        # Call update ONCE here after фрейм_дежурный is created
        self._обновить_поле_ввода_дежурный()

        # --- Start of Дневальные Section ---
        # Check if dnavalnye are assigned for this post
        if self.данные_поста.get('дневальный', False):
            # Создаем фрейм для дневальных только если они нужны
            self.фрейм_дневальные = ttk.Frame(self.фрейм_поля_для_ввода)
            self.фрейм_дневальные.pack(side='top', fill='both', expand=True)

            # Фрейм для выбора количества (слева)
            self.фрейм_выбор_количества = ttk.Frame(self.фрейм_дневальные)
            self.фрейм_выбор_количества.pack(side='left', fill='y')

            # Лейбл "Дневальные"
            self.лейбл_дневальные = ttk.Label(self.фрейм_выбор_количества, text="Дневальные")
            # ширина 15
            self.лейбл_дневальные.configure(width=15)  # Set width to 15 characters
            self.лейбл_дневальные.pack(side='top')

            # Выбор количества дневальных (Spinbox)
            # Determine max quantity from loaded data, default to 0 if not available
            max_дневальные = self.данные_поста.get('дневальный_кол', 0)
            self.выбор_количества = ttk.Spinbox(
                self.фрейм_выбор_количества,
                from_=0,
                to=max_дневальные, # Use max quantity from data
                textvariable=self.количество_дневальных_var,
                width=5,
                command=self._обновить_поля_ввода_дневальные # Update fields on change
            )
            self.выбор_количества.pack(side='top')
            # Set initial quantity (e.g., to the max allowed or 0)
            # Устанавливаем начальное количество в 0, если дневальные не обязательны, или в макс, если обязательны
            # Пока оставим max_дневальные, но можно изменить логику при необходимости
            self.количество_дневальных_var.set(max_дневальные)

            # Фрейм для полей ввода дневальных (справа)
            self.фрейм_поля_ввода_дневальные = ttk.Frame(self.фрейм_дневальные)
            self.фрейм_поля_ввода_дневальные.pack(side='right', fill='both', expand=True)

            # Инициализируем поля ввода для дневальных
            self._обновить_поля_ввода_дневальные()
        else:
            # Если дневальные не назначаются, убедимся, что связанные переменные инициализированы
            # (хотя они уже инициализированы в начале __init__)
            self.фрейм_дневальные = None # Явно указываем, что фрейма нет
            self.количество_дневальных_var.set(0)
            self.поля_ввода_дневальные = []

        # --- End of Дневальные Section ---

        # Remove the duplicate variable definition at the end
        # self.тип_сотрудника_var = tk.StringVar(value="officer") # Remove this line

        # Устанавливаем начальное состояние элементов в зависимости от чекбокса
        self._обновить_состояние_элементов_в_зависимости_от_назначения()

    def _загрузить_данные_поста(self) -> dict:
        """Загружает данные поста из БД по ID"""
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
                # Создаем словарь с правильными ключами
                данные = {
                    'id': результат[0]['id'],
                    'наименование': результат[0]['наименование'],
                    'дежурный': bool(результат[0]['дежурный']),
                    'дежурный_кол': int(результат[0]['дежурный_кол'] or 0),
                    'дежурный_офицер': bool(результат[0]['дежурный_офицер']),
                    'дежурный_курсант': bool(результат[0]['дежурный_курсант']),
                    'дневальный': bool(результат[0]['дневальный']),
                    'дневальный_кол': int(результат[0]['дневальный_кол'] or 0)
                }
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

    def _обновить_поле_ввода_дежурный(self):
        """Обновляет поле ввода в зависимости от выбранного типа сотрудника"""
        if self.поле_ввода_дежурный:
            self.поле_ввода_дежурный.destroy()
            self.поле_ввода_дежурный = None # Reset to None

        selected_type = self.тип_сотрудника_var.get()
        can_assign_officer = self.данные_поста.get('дежурный_офицер', False)
        can_assign_cadet = self.данные_поста.get('дежурный_курсант', False)

        if selected_type == "officer" and can_assign_officer:
            self.поле_ввода_дежурный = ПоискОфицера(self.фрейм_дежурный)
        elif selected_type == "cadet" and can_assign_cadet:
            self.поле_ввода_дежурный = ПоискКурсанта(self.фрейм_дежурный)
        # else: # Если тип не выбран или не разрешен, поле не создается
        #     pass

        if self.поле_ввода_дежурный:
            self.поле_ввода_дежурный.pack(side='left', fill='x', expand=True, anchor='n') # Выравнивание по верхнему краю

    # --- New Method for Дневальные ---
    def _обновить_поля_ввода_дневальные(self):
        """Обновляет поля ввода для дневальных в зависимости от выбранного количества."""
        # Проверяем, существует ли фрейм для полей ввода дневальных
        if not hasattr(self, 'фрейм_поля_ввода_дневальные') or not self.фрейм_поля_ввода_дневальные:
            return # Ничего не делаем, если фрейм не был создан

        # Уничтожаем старые поля ввода
        for поле_ввода in self.поля_ввода_дневальные:
            поле_ввода.destroy()
        self.поля_ввода_дневальные.clear() # Очищаем список

        try:
            количество = self.количество_дневальных_var.get()
        except tk.TclError:
            количество = 0 # Handle cases where the value might be invalid temporarily

        # Создаем новые поля ввода
        for i in range(количество):
            поле_ввода = ПоискКурсанта(self.фрейм_поля_ввода_дневальные)
            поле_ввода.pack(side='top', fill='x', expand=True, pady=2) # Pack vertically with reduced padding
            self.поля_ввода_дневальные.append(поле_ввода)

    def _обновить_состояние_элементов_в_зависимости_от_назначения(self, *_):
        """Обновляет состояние и внешний вид элементов в зависимости от состояния чекбокса 'назначен'."""
        is_assigned = self.is_assigned_var.get()
        new_state = tk.NORMAL if is_assigned else tk.DISABLED
        # Изменяем цвет на более темный серый для неактивных элементов
        label_color = 'black' if is_assigned else '#666666'  # Темно-серый цвет

        # Обновляем основные метки
        self.name_label.configure(foreground=label_color)
        self.date_label.configure(foreground=label_color)

        # Обновляем элементы выбора типа сотрудника (радиокнопки)
        if hasattr(self, 'фрейм_выбор_типа_сотрудника') and self.фрейм_выбор_типа_сотрудника.winfo_exists():
            for widget in self.фрейм_выбор_типа_сотрудника.winfo_children():
                if isinstance(widget, ttk.Radiobutton):
                    widget.configure(state=new_state)
                    # Дополнительно настраиваем стиль для радиокнопок
                    widget.configure(style='Dim.TRadiobutton' if not is_assigned else 'TRadiobutton')
        
        # Обновляем метку дежурного
        if hasattr(self, 'лейбл_дежурный') and self.лейбл_дежурный and self.лейбл_дежурный.winfo_exists():
            self.лейбл_дежурный.configure(foreground=label_color)

        # Обновляем поле ввода дежурного
        if hasattr(self, 'поле_ввода_дежурный') and self.поле_ввода_дежурный and self.поле_ввода_дежурный.winfo_exists():
            try:
                if hasattr(self.поле_ввода_дежурный, 'set_enabled'):
                    self.поле_ввода_дежурный.set_enabled(is_assigned)
                else:
                    for child in self.поле_ввода_дежурный.winfo_children():
                        if isinstance(child, (ttk.Entry, ttk.Button)):
                            child.configure(state=new_state)
                        elif hasattr(child, 'set_enabled'):
                            child.set_enabled(is_assigned)
            except tk.TclError:
                pass

        # Обновляем элементы дневальных
        if hasattr(self, 'фрейм_дневальные') and self.фрейм_дневальные and self.фрейм_дневальные.winfo_exists():
            # Обновляем метку дневальных
            if hasattr(self, 'лейбл_дневальные') and self.лейбл_дневальные:
                self.лейбл_дневальные.configure(foreground=label_color)
            
            # Обновляем спинбокс выбора количества
            if hasattr(self, 'выбор_количества') and self.выбор_количества:
                self.выбор_количества.configure(state=new_state)
            
            # Обновляем поля ввода дневальных
            if hasattr(self, 'поля_ввода_дневальные'):
                for поле_ввода in self.поля_ввода_дневальные:
                    if поле_ввода and поле_ввода.winfo_exists():
                        try:
                            if hasattr(поле_ввода, 'set_enabled'):
                                поле_ввода.set_enabled(is_assigned)
                            else:
                                for child in поле_ввода.winfo_children():
                                    if isinstance(child, (ttk.Entry, ttk.Button)):
                                        child.configure(state=new_state)
                                    elif hasattr(child, 'set_enabled'):
                                        child.set_enabled(is_assigned)
                        except tk.TclError:
                            pass