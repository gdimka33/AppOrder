import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from БД_соединение import выполнить_запрос
from logger import logger

class РедактироватьДолжность(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Редактирование должности")
        self.geometry("500x400")  # Увеличим размер окна
        self.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Создание основного фрейма
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Поиск должности
        ttk.Label(main_frame, text="Поиск должности:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.поиск = ttk.Combobox(main_frame, width=40)
        self.поиск.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.поиск.bind('<<ComboboxSelected>>', self.выбор_должности)
        
        # Текущие данные
        ttk.Label(main_frame, text="Текущие данные:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.текущие_данные = ttk.Label(main_frame, text="")
        self.текущие_данные.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Наименование должности
        ttk.Label(main_frame, text="Новое наименование:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.наименование = ttk.Entry(main_frame, width=40)
        self.наименование.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Категории
        ttk.Label(main_frame, text="Категории:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        categories_frame = ttk.Frame(main_frame)
        categories_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.категории = {
            'офицер': tk.BooleanVar(),
            'работник': tk.BooleanVar(),
            'курсант': tk.BooleanVar()
        }
        
        for i, (key, var) in enumerate(self.категории.items()):
            ttk.Checkbutton(categories_frame, text=key.capitalize(), variable=var).grid(
                row=i, column=0, sticky=tk.W
            )
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить изменения", command=self.сохранить).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(buttons_frame, text="Отмена", command=self.destroy).grid(
            row=0, column=1, padx=5
        )
        
        # Загрузка списка должностей
        self.загрузить_список_должностей()
        self.должность_id = None  # Добавим атрибут для хранения ID
        
        # Центрирование окна
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
    def center_window(self):
        """Центрирует окно относительно экрана"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def загрузить_список_должностей(self):
        """Загружает список должностей в комбобокс"""
        try:
            result = выполнить_запрос("SELECT id, наименование FROM должности ORDER BY наименование")
            self.должности = {row['наименование']: row['id'] for row in result}
            self.поиск['values'] = list(self.должности.keys())
        except Exception as e:
            logger.error(f"Ошибка при загрузке списка должностей: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить список должностей")
            
    def выбор_должности(self, event=None):
        """Обработчик выбора должности из списка"""
        выбранное = self.поиск.get()
        if выбранное in self.должности:
            self.должность_id = self.должности[выбранное]
            self.загрузить_данные()
            
    def загрузить_данные(self):
        """Загружает данные выбранной должности"""
        try:
            if not self.должность_id:
                return
                
            result = выполнить_запрос(
                "SELECT наименование, категории FROM должности WHERE id = ?",
                (self.должность_id,)
            )
            
            if not result:
                messagebox.showerror("Ошибка", "Должность не найдена")
                return
                
            должность = result[0]
            
            # Отображаем текущие данные
            категории = json.loads(должность['категории'])
            текущие = f"Наименование: {должность['наименование']}\nКатегории: {', '.join(категории)}"
            self.текущие_данные.config(text=текущие)
            
            # Заполняем поля для редактирования
            self.наименование.delete(0, tk.END)
            self.наименование.insert(0, должность['наименование'])
            
            # Сбрасываем все чекбоксы
            for var in self.категории.values():
                var.set(False)
            
            # Устанавливаем нужные категории
            for категория in категории:
                if категория in self.категории:
                    self.категории[категория].set(True)
                    
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных должности: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            
    def сохранить(self):
        """Сохраняет изменения должности в базу данных"""
        try:
            наименование = self.наименование.get().strip().lower()
            
            if not наименование:
                messagebox.showwarning("Предупреждение", "Введите наименование должности")
                return
            
            # Формируем список категорий
            категории = [
                key for key, var in self.категории.items() if var.get()
            ]
            
            if not категории:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы одну категорию")
                return
            
            # Проверяем существование должности с таким именем (кроме текущей)
            result = выполнить_запрос(
                "SELECT id FROM должности WHERE наименование = ? AND id != ?",
                (наименование, self.должность_id)
            )
            
            if result:
                messagebox.showwarning("Предупреждение", "Должность с таким названием уже существует")
                return
            
            # Сохраняем изменения
            выполнить_запрос(
                "UPDATE должности SET наименование = ?, категории = ? WHERE id = ?",
                (наименование, json.dumps(категории), self.должность_id)
            )
            
            logger.info(f"Обновлена должность: {наименование}")
            messagebox.showinfo("Успех", "Изменения сохранены")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении должности: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {str(e)}")

def открыть_форму():
    root = tk.Tk()
    app = РедактироватьДолжность(root)
    app.wait_window()
    root.destroy()

if __name__ == "__main__":
    открыть_форму()
