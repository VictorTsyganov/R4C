import sqlite3
from datetime import datetime, timedelta
from json import loads

import pandas as pd
import xlwt
from django.http import FileResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Robot
from .validators import validate_robot


@csrf_exempt
def create_robot(request):
    'функция создания данных для робота.'
    if request.method == 'POST':
        data = validate_robot(loads(request.body))
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
            robot_json = robot.__dict__
            robot_json.pop('_state')
            return JsonResponse(robot_json)
        return HttpResponseBadRequest(
            'Данный робот был создан ранее.'
        )
    return HttpResponseBadRequest(
        'Используйте метод POST для данного запроса.'
    )


@csrf_exempt
def download_report(request):
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
            for i in range(3):
                sheet.write(0, i, df.columns.values[i])
            num = 1
            for item in df.values:
                if not item[0] == sheet_name:
                    sheet_name = item[0]
                    sheet = book.add_sheet(sheet_name)
                    for i in range(3):
                        sheet.write(0, i, df.columns.values[i])
                    num = 1
                row = sheet.row(num)
                for i in range(3):
                    row.write(i, item[i])
                num += 1
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
