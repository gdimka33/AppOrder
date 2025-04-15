from БД_соединение import выполнить_запрос
from logger import logger

# Описание структуры таблиц базы данных
TABLES = {
    'офицеры': '''
        CREATE TABLE IF NOT EXISTS офицеры (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            имя TEXT NOT NULL,
            фамилия TEXT NOT NULL,
            отчество TEXT,
            звание_id INTEGER,
            должность_id INTEGER,
            подразделение_id INTEGER,
            состояние_сод INTEGER DEFAULT 0,
            состояние_псод INTEGER DEFAULT 0,
            FOREIGN KEY (звание_id) REFERENCES звания (id),
            FOREIGN KEY (должность_id) REFERENCES должности (id),
            FOREIGN KEY (подразделение_id) REFERENCES подразделения (id)
        )
    ''',
    
    'курсанты': '''
        CREATE TABLE IF NOT EXISTS курсанты (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            имя TEXT NOT NULL,
            фамилия TEXT NOT NULL,
            отчество TEXT,
            звание_id INTEGER,
            должность_id INTEGER,
            подразделение_id INTEGER,
            год_набора INTEGER NOT NULL,
            состояние_сод INTEGER DEFAULT 0,
            состояние_псод INTEGER DEFAULT 0,
            FOREIGN KEY (звание_id) REFERENCES звания (id),
            FOREIGN KEY (должность_id) REFERENCES должности (id),
            FOREIGN KEY (подразделение_id) REFERENCES подразделения (id)
        )
    ''',
    
    'звания': '''
        CREATE TABLE IF NOT EXISTS звания (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            наименование TEXT NOT NULL,
            категория TEXT NOT NULL,
            CONSTRAINT check_категория CHECK (категория IN ('курсант', 'офицер', 'общее'))
        )
    ''',

    'должности': '''
        CREATE TABLE IF NOT EXISTS должности (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            наименование TEXT NOT NULL,
            категория TEXT NOT NULL,
            CONSTRAINT check_категория CHECK (категория IN ('курсант', 'офицер', 'общее'))
        )
    ''',

    'подразделения': '''
        CREATE TABLE IF NOT EXISTS подразделения (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            наименование TEXT NOT NULL,
            абривиатура TEXT
        )
    ''',

    'история_перемещения_сотрудников': '''
        CREATE TABLE IF NOT EXISTS история_перемещения_сотрудников (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            сотрудник_id INTEGER NOT NULL,
            сотрудник_type TEXT NOT NULL,  -- 'офицер' или 'курсант'
            change_type TEXT NOT NULL,  -- 'звание' или 'должность'
            звание_id INTEGER,
            должность_id INTEGER,
            подразделение_id INTEGER,
            дата_начала DATE NOT NULL,
            дата_окончание DATE,
            FOREIGN KEY (звание_id) REFERENCES звания (id),
            FOREIGN KEY (должность_id) REFERENCES должности (id),
            FOREIGN KEY (подразделение_id) REFERENCES подразделения (id)
        )
    ''',
    'приказы': '''
        CREATE TABLE IF NOT EXISTS приказы (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            дата_создания DATE NOT NULL,
            дата_регистрации DATE,
            номер_регистрации TEXT,
            исполнитель_id INTEGER NOT NULL,
            руководитель_id INTEGER NOT NULL,
            название TEXT NOT NULL,
            текст_приказа TEXT NOT NULL,
            тип_приказа TEXT NOT NULL,
            список_лиц_согласования TEXT,
            FOREIGN KEY (исполнитель_id) REFERENCES офицеры (id),
            FOREIGN KEY (руководитель_id) REFERENCES офицеры (id)
        )
    ''',
}

def проверка_создание_таблиц():
    """Проверяет существование необходимых таблиц в базе данных и создает отсутствующие"""
    try:
        # Сначала создаем справочные таблицы
        справочные_таблицы = {k: v for k, v in TABLES.items() if k in ['звания', 'должности', 'подразделения']}
        for имя_таблицы, sql_запрос in справочные_таблицы.items():
            выполнить_запрос(sql_запрос)
            logger.info(f"Проверена/создана таблица {имя_таблицы}")
        
        # Затем создаем основные таблицы, которые зависят от справочных
        основные_таблицы = {k: v for k, v in TABLES.items() if k not in ['звания', 'должности', 'подразделения']}
        for имя_таблицы, sql_запрос in основные_таблицы.items():
            выполнить_запрос(sql_запрос)
            logger.info(f"Проверена/создана таблица {имя_таблицы}")
        
        # Заполняем справочники начальными данными
        _заполнить_справочник_званий()
        _заполнить_справочник_должностей()
        _заполнить_справочник_подразделений()
        
        # Проверяем, что таблицы созданы корректно, используя более надежный метод
        for имя_таблицы in TABLES.keys():
            try:
                # Проверяем существование таблицы, пытаясь выполнить простой запрос
                выполнить_запрос(f"SELECT 1 FROM {имя_таблицы} LIMIT 1")
                logger.info(f"Структура таблицы {имя_таблицы} проверена успешно")
            except Exception as e:
                logger.error(f"Ошибка при проверке таблицы {имя_таблицы}: {e}")
                raise Exception(f"Не удалось проверить таблицу {имя_таблицы}")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке/создании таблиц: {e}")
        raise

def _заполнить_справочник_званий():
    """Заполняет справочник званий начальными данными"""
    звания = [
        # Звания для курсантов
        ('рядовой', 'курсант'),
        ('ефрейтор', 'курсант'),
        ('младший сержант', 'курсант'),
        ('сержант', 'курсант'),
        ('старший сержант', 'курсант'),
        ('старшина', 'курсант'),
        
        # Общие звания
        ('прапорщик', 'общее'),
        ('старший прапорщик', 'общее'),
        
        # Звания для офицеров
        ('младший лейтенант', 'офицер'),
        ('лейтенант', 'офицер'),
        ('старший лейтенант', 'офицер'),
        ('капитан', 'офицер'),
        ('майор', 'офицер'),
        ('подполковник', 'офицер'),
        ('полковник', 'офицер')
    ]
    
    try:
        # Очищаем таблицу перед заполнением
        выполнить_запрос("DELETE FROM звания")
        
        # Заполняем таблицу данными
        for звание, категория in звания:
            выполнить_запрос(
                "INSERT INTO звания (наименование, категория) VALUES (?, ?)",
                (звание.lower(), категория)
            )
        logger.info("Справочник званий успешно заполнен")
    except Exception as e:
        logger.error(f"Ошибка при заполнении справочника званий: {e}")
        raise

def _заполнить_справочник_должностей():
    """Заполняет справочник должностей начальными данными"""
    должности = [
        # Должности для курсантов
        ('курсант', 'курсант'),
        ('командир отделения', 'курсант'),
        ('заместитель командира взвода', 'курсант'),
        ('старшина курса', 'курсант'),
        
        # Должности для офицеров
        ('начальник института', 'офицер'),
        ('заместитель начальника института по учебной работе', 'офицер'),
        ('заместитель начальника института по служебно-боевой подготовке', 'офицер'),
        ('заместитель начальника института по тылу', 'офицер'),
        ('заместитель начальника института по кадрам', 'офицер'),
        ('начальник службы', 'офицер'),
        ('начальник отдела', 'офицер'),
        ('заместитель начальника отдела', 'офицер'),
        ('начальник отделения', 'офицер'),
        ('начальник факультета', 'офицер'),
        ('заместитель начальника факультета', 'офицер'),
        ('начальник кафедры', 'офицер'),
        ('заместитель начальника кафедры', 'офицер'),
        ('начальник курса', 'офицер'),
        ('заместитель начальника курса', 'офицер'),
        ('начальник архива', 'офицер'),
        ('начальник секретариата', 'офицер'),
        ('начальник дежурной службы', 'офицер'),
        ('старший оперативный дежурный', 'офицер'),
        ('контролер КПП', 'офицер'),
        ('помощник начальника института по строительству', 'офицер'),
        ('ученый секретарь', 'офицер'),
        ('старший юрисконсульт', 'офицер'),
        ('юрисконсульт', 'офицер'),
        ('инспектор', 'офицер'),
        ('старший инспектор', 'офицер'),
        ('младший инспектор', 'офицер'),
        ('профессор', 'офицер'),
        ('доцент', 'офицер'),
        ('старший преподаватель', 'офицер'),
        ('преподаватель', 'офицер'),
        ('старший преподаватель-методист', 'офицер'),
        ('преподаватель-методист', 'офицер'),
        ('командир взвода', 'офицер'),
        ('начальник кабинета', 'офицер'),
        ('старший инженер', 'офицер'),
        ('инженер', 'офицер'),
        ('инженер-программист', 'офицер'),
        ('старший бухгалтер', 'офицер'),
        ('бухгалтер', 'офицер'),
        ('старший психолог', 'офицер'),
        ('психолог', 'офицер'),
        ('начальник клуба', 'офицер'),
        ('дирижер оркестра', 'офицер'),
        ('начальник пресс-службы', 'офицер'),
        ('начальник библиотеки', 'офицер'),
        ('начальник научного центра', 'офицер'),
        ('старший научный сотрудник', 'офицер'),
        ('научный сотрудник', 'офицер'),
        ('начальник редакционно-издательского отдела', 'офицер'),
        ('старший редактор', 'офицер'),
        ('редактор', 'офицер'),
        ('начальник полиграфического отделения', 'офицер'),
        ('начальник службы вещевого обеспечения', 'офицер'),
        ('начальник столовой', 'офицер'),
        ('водитель-сотрудник', 'офицер'),
        ('заведующий кафедрой', 'офицер'),
        ('декан', 'офицер'),
        ('начальник филиала-врач', 'офицер'),
        ('врач-терапевт', 'офицер'),
        ('фельдшер', 'офицер'),
        ('делопроизводитель', 'офицер'),
        ('документовед', 'офицер'),
        ('специалист по учебно-методической работе', 'офицер'),
        ('диспетчер', 'офицер'),
        ('библиотекарь', 'офицер'),
        ('библиограф', 'офицер'),
        ('заведующий складом', 'офицер'),
        ('заведующий производством', 'офицер'),
        ('товаровед', 'офицер'),
        ('технический редактор', 'офицер'),
        ('главный специалист', 'офицер'),
        ('медсестра', 'офицер'),
        ('фармацевт', 'офицер'),
        ('водитель', 'офицер'),
        ('комендант зданий', 'офицер'),
        ('портной', 'офицер'),
        ('заведующий', 'офицер'),
        ('инженер-энергетик', 'офицер'),
        ('техник', 'офицер'),
        ('электромонтер', 'офицер'),
        ('монтажник', 'офицер'),
    ]
    
    try:
        # Очищаем таблицу перед заполнением
        выполнить_запрос("DELETE FROM должности")
        
        # Заполняем таблицу данными
        for должность, категория in должности:
            выполнить_запрос(
                "INSERT INTO должности (наименование, категория) VALUES (?, ?)",
                (должность.lower(), категория)
            )
        logger.info("Справочник должностей успешно заполнен")
    except Exception as e:
        logger.error(f"Ошибка при заполнении справочника должностей: {e}")
        raise

def _заполнить_справочник_подразделений():
    """Заполняет справочник подразделений начальными данными"""
    подразделения = [
        # Список подразделений с аббривиатурами
        ('Руководство института', None),
        ('Организационно-аналитическая служба', None),
        ('Ученый совет', None),
        ('Юридическое отделение', None),
        ('Секретариат', None),
        ('Архив', None),
        ('Дежурная служба', 'ДС'),
        ('Служба организации мобилизационной подготовки и гражданской обороны', 'СОМП и ГО'),
        ('Служба ведомственной пожарной охраны', 'СВПО'),
        ('Финансово-экономический отдел', 'ФЭО'),
        ('Группа капитального строительства', 'ГКС'),
        ('Учебный отдел', None),
        ('Отделение планирования и методического обеспечения образовательного процесса', 'ОПиМООП'),
        ('Отдел менеджмента и контроля качества образовательного процесса', 'ОМиККОП'),
        ('Отдел по внедрению и использованию технических средств обучения', 'ОВиИТСО'),
        ('Кафедра боевой и тактико-специальной подготовки', 'БиТСП'),
        ('Кафедра гуманитарных и социально-экономических дисциплин', 'ГиСЭД'),
        ('Кафедра профессиональной языковой подготовки', 'ПЯП'),
        ('Кафедра психологии и педагогики профессиональной деятельности', 'ПиППД'),
        ('Кафедра специальной техники и информационных технологий', 'СТиИТ'),
        ('Кафедра физической подготовки', 'ФП'),
        ('Юридический факультет', 'ЮФ'),
        ('Отделение очного обучения', 'ООО'),
        ('Отделение заочного обучения', 'ОЗО'),
        ('Кафедра государственно-правовых дисциплин', 'ГПД'),
        ('Кафедра гражданско-правовых дисциплин ЮФ', 'КГрПД ЮФ'),
        ('Кафедра оперативно-розыскной деятельности ЮФ', 'КОРД ЮФ'),
        ('Кафедра организации режима и надзора ЮФ', 'КОРН ЮФ'),
        ('Кафедра уголовного права и криминологии ЮФ', 'КУПК ЮФ'),
        ('Кафедра уголовно-процессуального права и криминалистики ЮФ', 'КУППК ЮФ'),
        ('Кафедра уголовно-исполнительного права ЮФ', 'КУИП ЮФ'),
        ('Кафедра управления и административно-правовых дисциплин ЮФ', 'КУАПД ЮФ'),
        ('Кафедра организации деятельности оперативных аппаратов УИС и специальных мероприятий ЮФ', 'КОДОА ЮФ'),
        ('Учебно-строевые подразделения', 'УСП'),
        ('Факультет профессионального обучения и дополнительного профессионального образования', 'ФПОДПО'),
        ('Отдел кадров', 'ОК'),
        ('Отделение комплектования постоянного состава', 'ОКПС'),
        ('Отделение комплектования переменного состава', 'ОКПС'),
        ('Отдел воспитательной и социальной работы с личным составом', 'ОВСРЛС'),
        ('Отделение психологического обеспечения', 'ОПО'),
        ('Группа организации работы по противодействию коррупции и инспекции по личному составу', 'ГОРПК'),
        ('Клуб', 'КЛУБ'),
        ('Пресс-служба', 'ПС'),
        ('Библиотека', 'БИБ'),
        ('Служба связи', 'СС'),
        ('Научный центр', 'НЦ'),
        ('Организационно-научное отделение', 'ОНО'),
        ('Редакционно-издательский отдел', 'РИО'),
        ('Отдел тылового обеспечения', 'ОТО'),
        ('Служба государственного оборонного заказа и государственных закупок', 'СГОЗ'),
        ('Квартирно-эксплуатационное отделение', 'КЭО'),
        ('Служба вещевого обеспечения', 'СВО'),
        ('Отделение продовольственного обеспечения', 'ОПО'),
        ('Отделение автомобильного транспорта', 'ОАТ'),
        ('Факультет права и управления', 'ФПУ'),
        ('Кафедра теории и истории государства и права', 'КТИГП'),
        ('Кафедра публично-правовых дисциплин', 'КППД'),
        ('Кафедра частноправовых дисциплин', 'КЧД'),
        ('Кафедра управления и информационных технологий', 'КУИТ'),
        ('Отделение очного обучения ФПУ', 'ООО ФПУ'),
        ('Отделение заочного обучения ФПУ', 'ОЗО ФПУ'),
        ('Служба вооружения', 'СВ'),
        ('Отдел по защите государственной тайны', 'ОЗГТ'),
        ('Группа технической защиты информации', 'ГТЗИ'),
        ('Секретная библиотека', 'СБ'),
        ('Филиал МЧ-3 ФКУЗ МСЧ-33 ФСИН России', 'МЧ-3')
    ]
    
    try:
        # Проверяем, есть ли уже данные в таблице
        результат = выполнить_запрос("SELECT COUNT(*) FROM подразделения")
        if результат and результат[0][0] > 0:
            logger.info("Справочник подразделений уже заполнен")
            return
            
        # Заполняем таблицу данными
        for наименование, абривиатура in подразделения:
            выполнить_запрос(
                "INSERT INTO подразделения (наименование, абривиатура) VALUES (?, ?)",
                (наименование.lower(), абривиатура)
            )
        logger.info("Справочник подразделений успешно заполнен")
    except Exception as e:
        logger.error(f"Ошибка при заполнении справочника подразделений: {e}")
        raise

# Выполняем проверку при импорте модуля
if __name__ == "__main__":
    проверка_создание_таблиц()
