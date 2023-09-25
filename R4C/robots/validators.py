import re

from datetime import datetime


MODEL_VERSION: str = r'^[0-9A-Za-zА-ЯЁа-яё]{1,2}$'
CREATED: str = (
    r'^[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01]) '
    '([0-1]\d|2[0-3])(:[0-5]\d){2}$'
)


def validate_robot(data):
    """Производит валидацию входных данных при создании робота."""
    for item in ('model', 'version', 'created'):
        if item not in data.keys():
            return f'Поле {item} является обязательным для ввода данных'
        if not item == 'created':
            if not re.fullmatch(MODEL_VERSION, data.get(item)):
                return (
                    f'Для поля {item} укажите значение,'
                    'которое удовлетворяет критериям:\n'
                    '    - длина от 1 до 2 символов;\n'
                    '    - включает только цифры (0-9) '
                    'или буквы (a-z)(A-Z)(а-я)(А-Я).'
                )
        else:
            if not re.fullmatch(CREATED, data.get(item)):
                return (
                    f'Для поля {item} укажите значение,'
                    'которое соответствует виду 2022-12-31 23:59:59'
                )
            if str(datetime.today()) < data.get(item):
                return (
                    f'Для поля {item} нельзя указывать значение,'
                    'больше текущей даты и времени.'
                )
    return data
