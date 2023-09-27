import sqlite3
from datetime import datetime, timedelta
from json import JSONDecodeError, loads

import pandas as pd
import xlwt
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order
from R4C import settings

from .models import Robot
from .validators import validate_robot


@csrf_exempt
def create_robot(request):
    """Функция создания данных для робота."""
    if request.method == 'POST':
        try:
            data = validate_robot(loads(request.body))
        except JSONDecodeError:
            return HttpResponseBadRequest(
                'Запрос отправлен без необходимых данных.\n'
                'Нужны данные в формате JSON, например, \n'
                '{"model":"R2","version":"D2","created":"2022-12-31 23:59:59"}'
            )
        try:
            model = data.get('model')
            version = data.get('version')
            serial = f'{model}-{version}'
            created = data.get('created')
            robot, create = Robot.objects.get_or_create(
                model=model,
                version=version,
                serial=serial,
                created=created,
            )
        except AttributeError:
            return HttpResponseBadRequest(data)
        if create:
            orders = Order.objects.filter(robot_serial=serial)
            if orders:
                send_mail(
                    subject=f'Robot serial number {serial}.',
                    message=(
                        'Добрый день!\n'
                        'Недавно вы интересовались нашим роботом модели '
                        f'{model}, версии {version}.\n'
                        'Этот робот теперь в наличии. Если вам подходит '
                        'этот вариант - пожалуйста, свяжитесь с нами.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[orders[0].customer.email]
                )
                orders[0].customer.delete()
            robot_json = robot.__dict__
            robot_json.pop('_state')
            return JsonResponse(robot_json)
        return HttpResponseBadRequest(
            'Данный робот был создан ранее.'
        )
    return HttpResponseBadRequest(
        'Используйте метод POST для данного запроса.'
    )


def create_header_start_row(sheet, df):
    """Функция создания заголовка и перехода на новую строчку."""
    for i in range(3):
        sheet.write(0, i, df.columns.values[i])
    return 1


@csrf_exempt
def download_report(request):
    """Функция выгрузки отчета о создании роботов за неделю."""
    if request.method == 'GET':
        today = datetime.today()
        week = timedelta(weeks=1)
        report_date = today - week
        report_name = (
            'Отчет по производству роботов с '
            f'{report_date.strftime("%d.%m.%Y")} до '
            f'{today.strftime("%d.%m.%Y")}'
        )
        con = sqlite3.connect('db.sqlite3')
        df = pd.read_sql(
            'SELECT model, version, '
            'COUNT(serial) '
            'FROM robots_robot '
            f'WHERE created >= "{report_date}" '
            'GROUP BY serial', con
        )
        df.columns = ['Модель', 'Версия', 'Количество за неделю']
        try:
            book = xlwt.Workbook(encoding="utf-8")
            sheet_name = df.values[0][0]
            sheet = book.add_sheet(sheet_name)
            row_num = create_header_start_row(sheet, df)
            for item in df.values:
                if not item[0] == sheet_name:
                    sheet_name = item[0]
                    sheet = book.add_sheet(sheet_name)
                    row_num = create_header_start_row(sheet, df)
                row = sheet.row(row_num)
                for i in range(3):
                    row.write(i, item[i])
                row_num += 1
            filename = f'robots/reports/{report_name}.xls'
            book.save(filename)
            return FileResponse(open(filename, "rb"))
        except IndexError:
            return HttpResponseBadRequest(
                'За последнюю неделю не было произведено ни одного робота.'
            )
    return HttpResponseBadRequest(
        'Используйте метод GET для данного запроса.'
    )
