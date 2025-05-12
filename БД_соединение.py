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

def выполнить_запрос(sql, params=None):
    """
    Выполняет SQL запрос к базе данных
    Args:
        sql (str): SQL запрос
        params (tuple, dict, optional): Параметры запроса
    Returns:
        list: Результат запроса в виде списка словарей
    """
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DATABASE_PATH)
        # Включаем поддержку словарей
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        
        # # Логируем запрос
        # logger.debug(f"SQL запрос: {sql}")
        # if params:
        #     logger.debug(f"Параметры: {params}")
            
        # Выполняем запрос
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
            
        # Если это SELECT запрос
        if sql.strip().upper().startswith('SELECT'):
            # Получаем результаты и описание столбцов
            rows = cursor.fetchall()
            
            # Особая обработка для COUNT запросов
            if sql.strip().upper().startswith('SELECT COUNT'):
                return rows[0][0] if rows else 0
                
            # Для остальных SELECT запросов преобразуем в словари
            columns = [description[0] for description in cursor.description]
            результат = []
            for row in rows:
                row_dict = {}
                for idx, value in enumerate(row):
                    col_name = columns[idx].lower()
                    row_dict[col_name] = value
                результат.append(row_dict)
                
            return результат
        else:
            # Для остальных запросов (INSERT, UPDATE, DELETE)
            conn.commit()
            return []
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        logger.error(f"SQL: {sql}")
        if params:
            logger.error(f"Параметры: {params}")
        conn.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


