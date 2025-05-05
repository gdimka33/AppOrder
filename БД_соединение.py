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

def выполнить_запрос(sql_запрос, параметры=None):
    """
    Выполняет SQL запрос к базе данных
    Args:
        sql_запрос (str): SQL запрос
        параметры (tuple, optional): Параметры запроса. Defaults to None.
    Returns:
        list: Результат запроса для SELECT или список словарей для запросов с RETURNING
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            # Устанавливаем row_factory для получения результатов в виде словаря
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            try:
                if параметры:
                    cursor.execute(sql_запрос, параметры)
                else:
                    cursor.execute(sql_запрос)
                
                # Для запросов SELECT возвращаем результат в виде списка словарей
                if sql_запрос.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                # Для INSERT с RETURNING возвращаем результат в виде списка словарей
                elif 'RETURNING' in sql_запрос.upper():
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                # Для остальных запросов возвращаем None
                else:
                    connection.commit()
                    return None
                    
            except sqlite3.Error as e:
                logger.error(f"Ошибка при выполнении запроса: {e}\nЗапрос: {sql_запрос}")
                connection.rollback()
                raise
                
    except sqlite3.Error as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        raise


