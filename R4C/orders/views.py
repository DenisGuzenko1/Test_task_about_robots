# Импорты необходимых модулей и функций Django.
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# Импорты форм и моделей, используемых в этом коде.
from customers.forms import CustomerForm
from customers.models import Customer
from robots.models import Robot
from .forms import OrderForm


# Основная функция для обработки заказа.
def order(request):
    robots = Robot.objects.all()
    unique_robots = {}

    for robot in robots:
        # Используем комбинацию модели, версии и серии как ключ
        robot_key = f"{robot.model}-{robot.version}-{robot.serial}"

        # Проверяем, есть ли такой робот в словаре
        if robot_key not in unique_robots:
            unique_robots[robot_key] = robot

    # Преобразуем словарь уникальных роботов обратно в список
    unique_robot_list = list(unique_robots.values())
    # Инициализация переменной для хранения ошибки "Робот не найден".
    robot_not_found_error = None

    # Получение уникальных значений моделей, версий и серийных номеров роботов.
    robot_models = Robot.objects.values_list('model', flat=True).distinct()
    robot_versions = Robot.objects.values_list('version', flat=True).distinct()
    robot_serials = Robot.objects.values_list('serial', flat=True).distinct()

    # Проверка, была ли отправлена форма методом POST.
    if request.method == 'POST':
        # Инициализация форм заказа и клиента с данными из запроса.
        order_form = OrderForm(request.POST)
        customer_form = CustomerForm(request.POST)

        # Проверка валидности обеих форм.
        if order_form.is_valid() and customer_form.is_valid():
            # Извлечение данных клиента из формы.
            customer_email = customer_form.cleaned_data['email']
            customer_name = customer_form.cleaned_data['name']
            customer_surname = customer_form.cleaned_data['surname']

            # Поиск существующего клиента или создание нового.
            customer, created = Customer.objects.get_or_create(
                email=customer_email,
                name=customer_name,
                surname=customer_surname
            )

            # Извлечение данных о роботе из формы.
            robot_model = order_form.cleaned_data['robot_model']
            robot_version = order_form.cleaned_data['robot_version']
            robot_serial = order_form.cleaned_data['robot_serial']

            # Попытка найти робота с заданными параметрами.
            try:
                robot = Robot.objects.get(
                    model=robot_model,
                    version=robot_version,
                    serial=robot_serial
                )
            except Robot.DoesNotExist:
                # Если робот не найден, установка сообщения об ошибке.
                robot_not_found_error = "Такого робота не существует"

            # Если робот не был найден, то продолжение выполнения заказа не выполняется.
            if robot_not_found_error is None:
                # Сохранение заказа, связанного с клиентом.
                order = order_form.save(commit=False)
                order.customer = customer
                order.save()

                # Подготовка сообщения для отправки на email клиента.
                subject = "Заказ робота"
                message = "Ваш заказ успешно оформлен."

                # Если робот доступен (quantity > 0), то уменьшение его количества и добавление заказа.
                if robot.quantity > 0:
                    robot.quantity -= 1
                    robot.orders.add(order)
                    robot.save()
                    message += f" Робот модели {robot_model}, версии {robot_version}, с серийным номером {robot_serial} будет отправлен вам."
                # Если робота нет в наличии (quantity == 0), то установка флага недоступности и добавление заказа.
                elif robot.quantity == 0:
                    robot.is_available = False
                    robot.orders.add(order)
                    robot.save()
                    message += f" Добрый день! \n  Робот модели {robot_model} и версии {robot_version} на данный момент отсутствует. \n Мы свяжемся с вами, когда он появится."

                # Подготовка данных для отправки электронной почты.
                from_email = "gbublik2003@gmail.com"
                recipient_list = [customer_email]

                # Отправка сообщения на email клиента.
                send_mail(subject, message, from_email, recipient_list)

                # Перенаправление пользователя на страницу "success".
                return redirect('success')
    else:
        # Инициализация пустых форм для отображения на странице.
        order_form = OrderForm()
        customer_form = CustomerForm()

    # Отображение страницы "index.html" с передачей данных на шаблон.
    return render(request, 'index.html', {
        'order_form': order_form,
        'customer_form': customer_form,
        'robot_not_found_error': robot_not_found_error,
        'robot_models': robot_models,
        'robot_versions': robot_versions,
        'robot_serials': robot_serials,
        'robots': unique_robot_list,
    })


# Функция для отображения страницы "success.html".
def success(request):
    return render(request, 'success.html')
