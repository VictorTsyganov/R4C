from json import JSONDecodeError, loads

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from customers.models import Customer
from robots.models import Robot

from .models import Order
from .validators import validate_order


@csrf_exempt
def create_order(request):
    """Функция создания заказа на покупку робота."""
    if request.method == 'POST':
        try:
            data = validate_order(loads(request.body))
        except JSONDecodeError:
            return HttpResponseBadRequest(
                'Запрос отправлен без необходимых данных.\n'
                'Нужны данные в формате JSON, например, \n'
                '{"email":"example@example.ru","robot_serial":"R2-D2"}'
            )
        try:
            email = data.get('email')
            serial = data.get('robot_serial')
            customer, _ = Customer.objects.get_or_create(email=email)
            robot = Robot.objects.filter(serial=serial)
            if not robot:
                Order.objects.get_or_create(
                    customer=customer,
                    robot_serial=serial
                )
                return HttpResponse(
                    f'Запрашенного робота с серийным номером {serial} '
                    'нет в наличии.\n По факту появления робота на нашем '
                    'складе, вы получите уведомление на указанный вами '
                    f'адрес электронной почты {email}.')
        except AttributeError:
            return HttpResponseBadRequest(data)
        return HttpResponse('Робот есть в наличии.')
    return HttpResponseBadRequest(
        'Используйте метод POST для данного запроса.'
    )
