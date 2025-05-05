import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from БД_соединение import выполнить_запрос
from logger import logger

class ДобавлениеДолжности(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавление должности")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Создание основного фрейма
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Наименование должности
        ttk.Label(main_frame, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.наименование = ttk.Entry(main_frame, width=40)
        self.наименование.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Категории
        ttk.Label(main_frame, text="Категории:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        categories_frame = ttk.Frame(main_frame)
        categories_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
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
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.сохранить).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(buttons_frame, text="Отмена", command=self.destroy).grid(
            row=0, column=1, padx=5
        )
        
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
        
    def сохранить(self):
        """Сохраняет новую должность в базу данных"""
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
            
            # Проверяем существование должности
            result = выполнить_запрос(
                "SELECT id FROM должности WHERE наименование = ?",
                (наименование,)
            )
            
            if result:
                messagebox.showwarning("Предупреждение", "Такая должность уже существует")
                return
            
            # Сохраняем новую должность
            выполнить_запрос(
                "INSERT INTO должности (наименование, категории) VALUES (?, ?)",
                (наименование, json.dumps(категории))
            )
            
            logger.info(f"Добавлена новая должность: {наименование}")
            messagebox.showinfo("Успех", "Должность успешно добавлена")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении должности: {e}")
            messagebox.showerror("Ошибка", f"Не удалось добавить должность: {str(e)}")

def открыть_форму():
    root = tk.Tk()
    app = ДобавлениеДолжности(root)
    app.focus_force()  # Принудительно устанавливаем фокус на окно
    app.mainloop()  # Запускаем главный цикл событий

if __name__ == "__main__":
    открыть_форму()