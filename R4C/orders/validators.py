import re

ROBOT_SERIAL: str = r'^[0-9A-Za-zА-ЯЁа-яё]{1,2}-[0-9A-Za-zА-ЯЁа-яё]{1,2}$'
EMAIL: str = (
    r'^(?=.{1,255}$)[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@'
    '[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$'
)


def validate_order(data):
    """Производит валидацию входных данных при создании заказа."""
    for item in ('email', 'robot_serial'):
        if item not in data.keys():
            return f'Поле {item} является обязательным для ввода данных'
        if item == 'email':
            if not re.fullmatch(EMAIL, data.get(item)):
                return (
                    f'Для поля {item} введите корректный '
                    'email, например, example@example.ru\n'
                    'Количество символов не должно превышать 255'
                )
        else:
            if not re.fullmatch(ROBOT_SERIAL, data.get(item)):
                return (
                    f'Для поля {item} укажите значение,'
                    'которое соответствует виду R2-D2'
                )
    return data
