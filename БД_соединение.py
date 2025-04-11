import sqlite3
import os
import sys

# Добавляем родительскую директорию в PYTHONPATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from logger import logger

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def подключение_базыданных():
    try:
        соединение = sqlite3.connect(DATABASE_PATH)
        # Row_factory позволяет получать данные в виде словаря, где можно обращаться к столбцам по имени
        # Пример: row['column_name'] вместо row[0]
        # Это делает код более читаемым и менее подверженным ошибкам при изменении структуры таблиц
        соединение.row_factory = sqlite3.Row
        return соединение
    except sqlite3.Error as error:
        logger.error(f"Ошибка при подключении к базе данных: {error}")
        raise # Обработка ошибок при подключении к базе данных

def создание_базыданных():
    try:
        if os.path.exists(DATABASE_PATH):
            return
        logger.info("База данных отсутствует, создаем новую")
        подключение = подключение_базыданных()
        logger.info("Создана новая база данных")
        подключение.close()
        
        # Импортируем и вызываем функцию создания таблиц после создания базы
        from БД_заполнение_при_создании import проверка_создание_таблиц
        проверка_создание_таблиц()
        
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")
        raise

def выполнить_запрос(query, parameters=None):
    """
    Выполняет SQL запрос к базе данных
    
    Args:
        query (str): SQL запрос
        parameters (tuple|dict|None): Параметры для SQL запроса
    
    Returns:
        list: Результат запроса для SELECT или None для других операций
    """
    try:
        with подключение_базыданных() as connection:
            cursor = connection.cursor()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
                
            # Если это SELECT запрос
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            
            # Для INSERT, UPDATE, DELETE запросов
            connection.commit()
            return None
            
    except sqlite3.Error as error:
        logger.error(f"Ошибка при выполнении запроса: {error}\nЗапрос: {query}")
        raise

# Инициализация базы данных при импорте модуля
создание_базыданных()
