from django.db.models import Count  # Для агрегации и подсчета количества комментариев

from django.shortcuts import redirect  # Для перенаправления пользователя на другую страницу

from django.urls import reverse  # Для генерации URL-адресов по имени маршрута

# Импортируем модели из текущего приложения
from blog.models import Comment, Post

# Константа для количества элементов на странице при пагинации
PAGE_PAGINATOR = 10


class CustomListMixin:
    """
    Миксин для списковых представлений (ListView).
    Предоставляет общую логику для отображения списка постов:
    - Оптимизация запросов с select_related
    - Подсчет количества комментариев для каждого поста
    - Пагинация (разбивка на страницы)
    """
    
    # Указываем модель, с которой работает миксин
    model = Post
    
    # Количество постов на одной странице при пагинации
    paginate_by = PAGE_PAGINATOR

    def get_queryset(self):
        """
        Возвращает оптимизированный QuerySet постов.
        """
        
        # Создаем QuerySet с оптимизацией запросов
        queryset = Post.objects.select_related(
            'category', 
            'location',
            'author'    
        ).annotate(
            # Добавляем поле comment_count с количеством комментариев для каждого поста
            comment_count=Count('comments') 
        )
        
        # Сортируем посты согласно настройкам в модели Post
        return queryset.order_by(*Post._meta.ordering)


class PostChangeMixin:
    """
    Миксин для представлений изменения постов (редактирование, удаление).
    Обеспечивает проверку прав доступа: только автор поста может его изменять.
    """
    
    # Модель, с которой работает миксин
    model = Post
    
    # Имя шаблона, который будет использоваться для отображения формы
    template_name = 'blog/create.html'
    
    # Имя параметра URL, который содержит идентификатор поста
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределяем метод dispatch для проверки прав доступа.
        Вызывается перед вызовом любого HTTP-метода (GET, POST и т.д.).
        """
        
        # Получаем объект поста и проверяем его автора
        if self.get_object().author != request.user:
            # Если пользователь не автор - перенаправляем на страницу поста
            return redirect('blog:post_detail', self.kwargs['post_id'])
        
        # Если пользователь автор - вызываем родительский метод dispatch
        return super().dispatch(request, *args, **kwargs)


class CommentChangeMixin:
    """
    Миксин для представлений изменения комментариев (редактирование, удаление).
    Обеспечивает проверку прав доступа: только автор комментария может его изменять.
    Также определяет URL для перенаправления после успешного действия.
    """
    
    # Модель, с которой работает миксин
    model = Comment
    
    # Имя шаблона для отображения формы работы с комментарием
    template_name = 'blog/comment.html'
    
    # Имя параметра URL, который содержит идентификатор комментария
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):

        if self.get_object().author != request.user:

            return redirect('blog:post_detail', self.kwargs['post_id'])
        
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного изменения комментария.
        Всегда возвращает на страницу поста, к которому относится комментарий.
        """
        
        # Генерируем URL страницы поста с помощью reverse
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])