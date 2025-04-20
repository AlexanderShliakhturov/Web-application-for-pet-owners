import json
from datetime import date, datetime

class CustomJSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для обработки дат"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def json_dumps(obj):
    """Сериализация объекта в JSON с поддержкой дат"""
    return json.dumps(obj, cls=CustomJSONEncoder)

def json_loads(s):
    """Десериализация JSON с поддержкой дат"""
    def datetime_parser(dct):
        for k, v in dct.items():
            if isinstance(v, str):
                try:
                    # Пробуем парсить как datetime
                    dct[k] = datetime.fromisoformat(v)
                except (ValueError, TypeError):
                    try:
                        # Пробуем парсить как date
                        dct[k] = date.fromisoformat(v)
                    except (ValueError, TypeError):
                        pass
        return dct
    
    return json.loads(s, object_hook=datetime_parser) 