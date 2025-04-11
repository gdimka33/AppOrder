import logging
import sys

def setup_logger():
    # Создаем логгер
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Форматирование логов
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s (Line: %(lineno)d) [%(filename)s]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для записи в файл
    log_file = 'filelog.log'  # Файл будет создан в корневой директории
    file_handler = logging.FileHandler(
        log_file, 
        mode='w',  # Перезапись файла при каждом запуске
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем экземпляр логгера
logger = setup_logger()