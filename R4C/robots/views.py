import xlwt
from django.db.models import Count
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone

from .models import Robot


# Функция для вычисления количества роботов по сериям за последнюю неделю
def calculate_robot_counts():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    # Запрос к базе данных для получения количества роботов по сериям за последнюю неделю
    series_counts = Robot.objects.filter(created__range=(start_date, end_date)) \
        .values('serial', 'version') \
        .annotate(count=Count('id')) \
        .distinct()

    # Возвращаем результат в виде словаря, ключами являются пары (serial, version), а значениями - количество
    return {(item['serial'], item['version']): item['count'] for item in series_counts}


# Функция для экспорта данных о роботах в формате Excel
def export_to_excel(request):
    # Создаем объект HttpResponse для отправки Excel-файла в ответе
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="robots.xls"'

    # Создаем новую рабочую книгу Excel
    wb = xlwt.Workbook(encoding='utf-8')
    date_style = xlwt.XFStyle()
    date_style.num_format_str = 'yyyy-mm-dd HH:mm:ss'

    # Получаем список уникальных моделей роботов
    models = Robot.objects.values_list('model', flat=True).distinct()

    for model in models:
        # Добавляем новый лист Excel для каждой модели робота
        ws = wb.add_sheet(model)

        row_num = 0
        columns = ['Model', 'Serial', 'Version', 'Series Count (Last Week)']

        # Заполняем первую строку листа заголовками столбцов
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title)

        # Получаем список роботов для текущей модели
        robots = Robot.objects.filter(model=model).values_list('model', 'serial', 'version')

        # Получаем подсчитанное количество роботов по сериям за последнюю неделю
        series_counts = calculate_robot_counts()

        unique_series_versions = set()
        for row in robots:
            series, version = row[1], row[2]
            if (series, version) not in unique_series_versions:
                unique_series_versions.add((series, version))
                row_num += 1
                for col_num, cell_value in enumerate(row):
                    ws.write(row_num, col_num, cell_value)
                count = series_counts.get((series, version), 0)
                ws.write(row_num, 3, count)

    # Сохраняем рабочую книгу в HttpResponse
    wb.save(response)
    return response


# Функция для получения списка роботов и отправки в формате JSON
def robot_list(request):
    # Получаем все объекты модели Robot из базы данных
    robots = Robot.objects.all()

    # Создаем список словарей с информацией о роботах
    data = [
        {
            'model': robot.model,
            'version': robot.version,
            'created': robot.created.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for robot in robots
    ]

    # Возвращаем данные в виде JSON-ответа
    return JsonResponse({'robots': data})
