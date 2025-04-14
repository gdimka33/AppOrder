import tkinter as tk
from tkinter import ttk
from logger import logger
from БД_соединение import выполнить_запрос
from кл_ИнформационноеОкно import ИнформационноеОкно
from tkinter import filedialog
from БД_добавление_из_файла import добавить_из_файла
from кл_ТаблицаСотрудников import ТаблицаСотрудников
from кл_ДобавлениеСотрудника import ДобавлениеСотрудника

class СписокСотрудников(ttk.Frame):
    """
    Класс для отображения списка сотрудников в центральном фрейме.
    Принимает параметр тип_сотрудника для фильтрации списка.
    """
    def __init__(self, родитель, тип_сотрудника, главное_окно=None):
        super().__init__(родитель)
        self.тип_сотрудника = тип_сотрудника
        self.главное_окно = главное_окно
        
        # Растягиваем фрейм на всю ширину и высоту родительского контейнера
        self.pack(fill='both', expand=True)
        
        # Устанавливаем заголовок главного окна
        if self.главное_окно:
            заголовок = f"Учет личного состава - Список {self._получить_название_типа()}"
            self.главное_окно.title(заголовок)
        
        # Создаем левый и правый фреймы
        self._создать_фреймы()
        
        # Проверяем наличие записей в базе данных
        self._проверить_наличие_записей()
        
        logger.info(f"Открыт список сотрудников: {self.тип_сотрудника}")
    
    def _получить_название_типа(self):
        """Возвращает название типа сотрудника в нужном падеже"""
        if self.тип_сотрудника == "офицер":
            return "офицеров"
        elif self.тип_сотрудника == "курсант":
            return "курсантов"
        else:
            return "сотрудников"
    
    def _получить_название_типа_ед(self):
        """Возвращает название типа сотрудника в единственном числе"""
        if self.тип_сотрудника == "офицер":
            return "офицера"
        elif self.тип_сотрудника == "курсант":
            return "курсанта"
        else:
            return "сотрудника"
    
    def _создать_фреймы(self):
        """Создает левый и правый фреймы"""
        # Создаем левый фрейм для таблицы
        self.Таблица_сотрудников = ttk.Frame(self)
        self.Таблица_сотрудников.pack(side='left', fill='both', expand=True)
        
        # Создаем правый фрейм для меню, прилипающий к правому краю
        self.Меню_списка_сотрудников = ttk.Frame(self, width=200)
        self.Меню_списка_сотрудников.pack(side='right', fill='y')
        # Фиксируем ширину правого фрейма
        self.Меню_списка_сотрудников.pack_propagate(False)
        
        # Создаем группу "Добавить" для кнопок
        группа_добавить = ttk.LabelFrame(self.Меню_списка_сотрудников, text="Добавить", padding=10)
        группа_добавить.pack(fill='x', pady=5, padx=5)
        
        # Добавляем кнопки в группу с учетом типа сотрудника
        текст_кнопки = f"Добавить {self._получить_название_типа_ед()}"
        ttk.Button(группа_добавить, text=текст_кнопки, command=self._добавить_сотрудника).pack(fill='x', pady=2)
        ttk.Button(группа_добавить, text="Добавить из файла", command=self._добавить_из_файла).pack(fill='x', pady=2)
    
    def _проверить_наличие_записей(self):
        """Проверяет наличие записей в базе данных и отображает таблицу или информационное окно"""
        try:
            # Определяем таблицу в зависимости от типа сотрудника
            таблица = "офицеры" if self.тип_сотрудника == "офицер" else "курсанты"
            
            # Выполняем запрос к базе данных
            запрос = f"SELECT COUNT(*) as count FROM {таблица}"
            результат = выполнить_запрос(запрос)
            
            # Проверяем количество записей
            количество = результат[0]['count'] if результат else 0
            
            # Очищаем фрейм таблицы
            for виджет in self.Таблица_сотрудников.winfo_children():
                виджет.destroy()
            
            if количество == 0:
                # Если записей нет, отображаем информационное окно
                self._показать_информацию_об_отсутствии_записей()
            else:
                # Создаем и отображаем таблицу сотрудников
                таблица_сотрудников = ТаблицаСотрудников(
                    parent=self.Таблица_сотрудников,
                    тип_сотрудника=self.тип_сотрудника
                )
                # Размещаем таблицу в фрейме
                таблица_сотрудников.pack(fill='both', expand=True)
                    
        except Exception as e:
            logger.error(f"Ошибка при проверке наличия записей: {e}")
            self._показать_информацию_об_ошибке(str(e))
    
    def _показать_информацию_об_отсутствии_записей(self):
        """Отображает информационное окно об отсутствии записей"""
        # Очищаем фрейм таблицы
        for виджет in self.Таблица_сотрудников.winfo_children():
            виджет.destroy()
        
        # Создаем форматированный текст для информационного окна
        форматированный_текст = [
            (f"В базе данных нет {self._получить_название_типа()}!\n\n", ["header"]),
            ("Для добавления записей вы можете:\n", ["bold"]),
            (f"1. Нажать кнопку \"Добавить {self._получить_название_типа_ед()}\" в правой панели\n", []),
            ("2. Импортировать данные из файла, нажав кнопку \"Добавить из файла\"\n", [])
        ]
        
        # Отображаем информационное окно
        ИнформационноеОкно(self.Таблица_сотрудников, форматированный_текст)
    
    def _показать_информацию_об_ошибке(self, текст_ошибки):
        """Отображает информационное окно с сообщением об ошибке"""
        # Очищаем фрейм таблицы
        for виджет in self.Таблица_сотрудников.winfo_children():
            виджет.destroy()
        
        # Создаем форматированный текст для информационного окна
        форматированный_текст = [
            ("Произошла ошибка при получении данных!\n\n", ["header", "red"]),
            ("Детали ошибки:\n", ["bold"]),
            (текст_ошибки, ["red"])
        ]
        
        # Отображаем информационное окно
        ИнформационноеОкно(self.Таблица_сотрудников, форматированный_текст)
    
    def _добавить_сотрудника(self):
        """Обработчик нажатия кнопки 'Добавить сотрудника'"""
        # Очищаем фрейм таблицы
        for виджет in self.Таблица_сотрудников.winfo_children():
            виджет.destroy()
        
        # Создаем и отображаем форму добавления сотрудника
        форма_добавления = ДобавлениеСотрудника(
            родитель=self.Таблица_сотрудников,
            тип_сотрудника=self.тип_сотрудника,
            callback=self._после_добавления_сотрудника
        )
        
        logger.info(f"Запрошено добавление {self.тип_сотрудника}")
    
    def _после_добавления_сотрудника(self, успех):
        """Обработчик события после добавления сотрудника"""
        # Обновляем список сотрудников
        self._проверить_наличие_записей()

    def _добавить_из_файла(self):
        """Обработчик нажатия кнопки 'Добавить из файла'"""
        # TODO : Реализовать проверку при повторном добавлении, сравнивает, отображает какие записи добавить с возможностью выбора, с подтверждением
        try:
            # Определяем название файла в зависимости от типа сотрудника
            название_файла = "Офицеры.xlsx" if self.тип_сотрудника == "офицер" else "Курсанты.xlsx"
            
            # Открываем диалог выбора файла
            путь_к_файлу = filedialog.askopenfilename(
                title=f"Выберите файл с данными",
                filetypes=[("Excel файлы", "*.xlsx")],
                initialfile=название_файла
            )
            
            if путь_к_файлу:  # если файл выбран
                # Вызываем функцию добавления из файла
                успех, сообщение = добавить_из_файла(self.тип_сотрудника, путь_к_файлу)
                
                # Очищаем фрейм таблицы
                for виджет in self.Таблица_сотрудников.winfo_children():
                    виджет.destroy()
                
                if успех:
                    # Создаем форматированный текст для успешного добавления
                    форматированный_текст = [
                        ("Успешное добавление данных!\n\n", ["header", "green"]),
                        (f"{сообщение}\n", ["normal"]),
                        ("\nНажмите любую клавишу для продолжения...", ["italic"])
                    ]
                    # После закрытия информационного окна обновляем список
                    ИнформационноеОкно(self.Таблица_сотрудников, форматированный_текст, 
                                     callback=self._проверить_наличие_записей)
                else:
                    # Создаем форматированный текст для ошибки
                    форматированный_текст = [
                        ("Ошибка при добавлении данных!\n\n", ["header", "red"]),
                        ("Детали ошибки:\n", ["bold"]),
                        (f"{сообщение}", ["red"])
                    ]
                    ИнформационноеОкно(self.Таблица_сотрудников, форматированный_текст)
                    
        except Exception as e:
            logger.error(f"Ошибка при добавлении из файла: {e}")
            self._показать_информацию_об_ошибке(str(e))

