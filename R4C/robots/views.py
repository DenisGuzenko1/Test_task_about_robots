import json
from datetime import datetime

import pytz
import xlwt
from django.db.models import Count
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order
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
@csrf_exempt
def create_robot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Проверка наличия всех обязательных полей
            required_fields = ['serial', 'model', 'version', 'created']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Поле {field} отсутствует в запросе'}, status=400)

            # Проверка правильности формата времени и будущей даты
            try:
                # Используем UTC временную зону
                created_datetime = datetime.strptime(data['created'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.UTC)
                current_datetime = datetime.now(pytz.UTC)
                if created_datetime > current_datetime:
                    return JsonResponse({'error': 'Дата создания не может быть в будущем'}, status=400)
            except ValueError:
                return JsonResponse({'error': 'Неверный формат времени (ожидается: YYYY-MM-DDTHH:MM:SS)'}, status=400)

            # Проверка длины полей 'version', 'model' и 'serial'
            if len(data['version']) > 2 or len(data['model']) > 2 or len(data['serial']) > 5:
                return JsonResponse(
                    {'error': 'Поля version, model и serial могут содержать максимум 2 и 5 символов соответственно'},
                    status=400)

            # Создаем запись о роботе в базе данных
            robot = Robot(
                serial=data['serial'],
                model=data['model'],
                version=data['version'],
                created=created_datetime,
                quantity=data.get('quantity', None),
                is_available=data.get('is_available', True)
            )
            robot.save()

            # Если в запросе есть информация о заказах, добавляем их к роботу
            if 'orders' in data:
                for order_id in data['orders']:
                    try:
                        order = Order.objects.get(id=order_id)
                        robot.orders.add(order)
                    except Order.DoesNotExist:
                        return JsonResponse({'error': f'Заказ с ID {order_id} не существует'}, status=400)

            return JsonResponse({'message': 'Робот успешно создан'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
