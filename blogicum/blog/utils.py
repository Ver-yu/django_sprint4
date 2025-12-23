from django.utils import timezone  # Для работы с датами и временем с учетом часового пояса

from .models import Post           # Модель Post из текущего приложения

from django.core.paginator import Paginator  # Для разбиения результатов на страницы

from django.db.models import Count           # Для агрегации и подсчета комментариев


def published_only(queryset=None): # --- 13 2.4 Параметр с значением по умолчанию
    """
    Фильтрует QuerySet, оставляя только опубликованные посты.
    Учитывает три критерия публикации:
    1. Пост должен быть помечен как опубликованный (is_published=True)
    2. Дата публикации должна быть в прошлом или настоящем (pub_date__lte=timezone.now())
    3. Категория поста также должна быть опубликована (category__is_published=True)
    """
    
    # Если queryset не передан, используем все посты
    if queryset is None:
        from .models import Post 
        queryset = Post.objects.all()
    

    # Применяем фильтры для отбора только опубликованных постов
    return queryset.filter(
        is_published=True,             
        pub_date__lte=timezone.now(),   
        category__is_published=True     
    )



def get_paginated_page(queryset, request, per_page=10): # --- 11
    """
    Создает пагинацию для QuerySet.
    Разбивает большой список объектов на страницы для удобного отображения.
    """
    
    # Создаем объект Paginator для разбиения QuerySet на страницы
    paginator = Paginator(queryset, per_page)
    
    # Получаем номер текущей страницы из GET-параметра 'page'
    page_number = request.GET.get('page')
    
    # Возвращаем объект страницы для указанного номера
    return paginator.get_page(page_number)



def get_posts_with_comments(show_all=False, queryset=None): # --- 9 2.3
    """
    Возвращает QuerySet постов с оптимизацией запросов и подсчетом комментариев.
    Выполняет две ключевые оптимизации:
    1. select_related - предзагружает связанные объекты (категория, местоположение, автор)
    2. annotate - подсчитывает количество комментариев для каждого поста
    """
    
    # Если queryset не передан, используем все посты
    if queryset is None:
        queryset = Post.objects.all()
    
    # Если не нужно показывать все посты, применяем фильтрацию published_only
    if not show_all: # Параметр для управления фильтрацией
        queryset = published_only(queryset)
    
    # Оптимизация запросов к базе данных
    queryset = queryset.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')  # Подсчитывает количество комментариев
    )
    
    # Сортировка постов согласно настройкам ordering в Meta классе модели Post
    return queryset.order_by(*Post._meta.ordering)