import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from logger import logger
from БД_соединение import выполнить_запрос
from кл_ИнформационноеОкно import ИнформационноеОкно
from ви_ПоискОфицера import ПоискОфицера

class ПриказСуточныйНаряд(ttk.Frame):
    """
    Класс для создания и редактирования суточного приказа.
    Отображает форму для заполнения данных приказа.
    """
    def __init__(self, родитель, главное_окно=None):
        super().__init__(родитель)
        self.главное_окно = главное_окно
        
        # Растягиваем фрейм на всю ширину и высоту родительского контейнера
        self.pack(fill='both', expand=True)
        
        # Устанавливаем заголовок главного окна
        if self.главное_окно:
            self.главное_окно.title("Учет личного состава - Создание суточного приказа")
        
        # Создаем фрейм для формы
        self._создать_фрейм()
        
        # Заполняем форму начальными данными
        self._заполнить_начальные_данные()
        
        logger.info("Открыта форма создания суточного приказа")
    
    def _создать_фрейм(self):
        """Создает фрейм для формы"""
        # Создаем основной контейнер
        основной_контейнер = ttk.Frame(self)
        основной_контейнер.pack(fill='both', expand=True)
        
        # Создаем фрейм для формы
        self.форма_приказа = ttk.Frame(основной_контейнер)
        self.форма_приказа.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Создаем элементы формы
        self._создать_элементы_формы()
    
    def _создать_элементы_формы(self):
        """Создает элементы формы для заполнения данных приказа"""
        # Создаем заголовок
        ttk.Label(self.форма_приказа, text="Создание суточного приказа", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Создаем фрейм для основных данных приказа
        основные_данные = ttk.LabelFrame(self.форма_приказа, text="Основные данные", padding=10)
        основные_данные.pack(fill='x', pady=5, padx=5)
        
        # Дата создания
        ttk.Label(основные_данные, text="Дата создания:").pack(anchor='w')
        self.дата_создания_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        ttk.Entry(основные_данные, textvariable=self.дата_создания_var, state='readonly').pack(fill='x', pady=2)
        
        # Дата регистрации
        ttk.Label(основные_данные, text="Дата регистрации:").pack(anchor='w')
        self.дата_регистрации_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        ttk.Entry(основные_данные, textvariable=self.дата_регистрации_var).pack(fill='x', pady=2)
        
        # Номер регистрации
        ttk.Label(основные_данные, text="Номер регистрации:").pack(anchor='w')
        self.номер_регистрации_var = tk.StringVar()
        ttk.Entry(основные_данные, textvariable=self.номер_регистрации_var).pack(fill='x', pady=2)
        
        # Создаем фрейм для выбора исполнителя и руководителя
        ответственные = ttk.LabelFrame(self.форма_приказа, text="Ответственные лица", padding=10)
        ответственные.pack(fill='x', pady=5, padx=5)
        
        # Исполнитель - используем виджет ПоискОфицера
        ttk.Label(ответственные, text="Исполнитель:").pack(anchor='w')
        self.исполнитель_фрейм = ttk.Frame(ответственные)
        self.исполнитель_фрейм.pack(fill='x', pady=2)
        self.исполнитель_виджет = ПоискОфицера(
            self.исполнитель_фрейм, 
            callback=self._обработать_выбор_исполнителя,
            placeholder="Введите фамилию исполнителя..."
        )
        
        # Руководитель - используем виджет ПоискОфицера
        ttk.Label(ответственные, text="Руководитель:").pack(anchor='w')
        self.руководитель_фрейм = ttk.Frame(ответственные)
        self.руководитель_фрейм.pack(fill='x', pady=2)
        self.руководитель_виджет = ПоискОфицера(
            self.руководитель_фрейм, 
            callback=self._обработать_выбор_руководителя,
            placeholder="Введите фамилию руководителя..."
        )
        
        # Лица для согласования (простое текстовое поле)
        ttk.Label(ответственные, text="Лица для согласования (через запятую):").pack(anchor='w')
        self.лица_согласования_var = tk.StringVar()
        ttk.Entry(ответственные, textvariable=self.лица_согласования_var).pack(fill='x', pady=2)
    
    def _обработать_выбор_исполнителя(self, офицер):
        """Обработчик выбора исполнителя"""
        logger.info(f"Выбран исполнитель: {офицер['отображение']}")
    
    def _обработать_выбор_руководителя(self, офицер):
        """Обработчик выбора руководителя"""
        logger.info(f"Выбран руководитель: {офицер['отображение']}")
    
    def _заполнить_начальные_данные(self):
        """Заполняет форму начальными данными из базы данных"""
        try:
            # Для виджетов ПоискОфицера не требуется предварительная загрузка данных,
            # так как они сами загружают данные при поиске
            pass
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных для приказа: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
    
    def _сохранить_приказ(self):
        """Сохраняет приказ в базу данных"""
        try:
            # Получаем данные из формы
            дата_создания = self.дата_создания_var.get()
            номер_регистрации = self.номер_регистрации_var.get()
            название = self.название_var.get()
            исполнитель = self.исполнитель_var.get()
            руководитель = self.руководитель_var.get()
            текст_приказа = self.текст_приказа.get("1.0", tk.END).strip()
            
            # Проверяем обязательные поля
            if not название or not текст_приказа:
                messagebox.showerror("Ошибка", "Необходимо заполнить название и текст приказа")
                return
            
            # Получаем ID исполнителя и руководителя
            исполнитель_id = self.офицеры_данные.get(исполнитель)
            руководитель_id = self.офицеры_данные.get(руководитель)
            
            if not исполнитель_id or not руководитель_id:
                messagebox.showerror("Ошибка", "Необходимо выбрать исполнителя и руководителя")
                return
            
            # Получаем выбранные лица согласования
            выбранные_индексы = self.список_лиц_согласования.curselection()
            лица_согласования = [self.список_лиц_согласования.get(i) for i in выбранные_индексы]
            
            # Преобразуем список лиц согласования в JSON строку
            список_лиц_согласования_json = json.dumps(лица_согласования, ensure_ascii=False)
            
            # Преобразуем дату в формат для базы данных (YYYY-MM-DD)
            try:
                дата_создания_obj = datetime.strptime(дата_создания, "%d.%m.%Y")
                дата_создания_бд = дата_создания_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                return
            
            # Сохраняем приказ в базу данных
            запрос = """
                INSERT INTO приказы (
                    дата_создания, дата_регистрации, номер_регистрации, 
                    исполнитель_id, руководитель_id, название, 
                    текст_приказа, тип_приказа, список_лиц_согласования
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            параметры = (
                дата_создания_бд,  # дата_создания
                дата_создания_бд,  # дата_регистрации (пока та же)
                номер_регистрации,
                исполнитель_id,
                руководитель_id,
                название,
                текст_приказа,
                "суточный",  # тип_приказа
                список_лиц_согласования_json
            )
            
            выполнить_запрос(запрос, параметры)
            
            # Показываем сообщение об успешном сохранении
            messagebox.showinfo("Успех", "Приказ успешно сохранен")
            
            # Очищаем форму или возвращаемся на предыдущий экран
            if self.главное_окно:
                # Возвращаемся на главный экран
                self.главное_окно.title("Учет личного состава")
                # Очищаем центральный фрейм
                for виджет in self.master.winfo_children():
                    виджет.destroy()
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении приказа: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить приказ: {e}")
    
    def _отмена(self):
        """Отменяет создание приказа и возвращается на предыдущий экран"""
        # Подтверждение отмены
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить создание приказа?"):
            if self.главное_окно:
                # Возвращаемся на главный экран
                self.главное_окно.title("Учет личного состава")
                # Очищаем центральный фрейм
                for виджет in self.master.winfo_children():
                    виджет.destroy()
    
    def _показать_информацию_об_ошибке(self, текст_ошибки):
        """Отображает информационное окно с сообщением об ошибке"""
        # Очищаем фрейм предпросмотра
        for виджет in self.предпросмотр_приказа.winfo_children():
            виджет.destroy()
        
        # Создаем форматированный текст для информационного окна
        форматированный_текст = [
            ("Произошла ошибка при получении данных!\n\n", ["header", "red"]),
            ("Детали ошибки:\n", ["bold"]),
            (текст_ошибки, ["red"])
        ]
        
        # Отображаем информационное окно
        ИнформационноеОкно(self.предпросмотр_приказа, форматированный_текст)