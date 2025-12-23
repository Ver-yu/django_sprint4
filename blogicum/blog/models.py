from django.contrib.auth import get_user_model

from django.db import models

# Добавляет общие поля is_published и created_at
from core.models import PublishedModel

# Получаем активную модель пользователя (стандартную User или кастомную)
User = get_user_model()

# Константа для ограничения длины строкового представления моделей
SYMBOL_CONSTRAINT = 30

# Константа для ограничения длины текста комментария в строковом представлении
LIMIT_FOR_COMMENT_TITLE = 20


class Location(PublishedModel):
    """
    Модель для хранения местоположений (географических мест).
    Используется для привязки постов к определенным местам.
    """
    
    # Поле для названия места, максимальная длина - 256 символов
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        # Настройки отображения модели в единственном числе в админке
        verbose_name = 'местоположение'
        # Настройки отображения модели во множественном числе в админке
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:SYMBOL_CONSTRAINT]


class Category(PublishedModel):
    """
    Модель для хранения категорий постов.
    Категории организуют посты по темам.
    """
    
    # Поле для заголовка категории
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    
    # Поле для подробного описания категории (неограниченный текст)
    description = models.TextField('Описание')
    
    # Поле для URL-идентификатора категории (человекочитаемая часть URL)
    slug = models.SlugField(
        unique=True, 
        verbose_name='Идентификатор',
        help_text=(  
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        # Настройки отображения модели в админке
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:SYMBOL_CONSTRAINT]



class Post(PublishedModel): #---
    """
    Основная модель для хранения публикаций (постов) в блоге.
    Содержит основной контент блога.
    """
    
    # Поле для заголовка поста
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    
    # Поле для основного текста поста
    text = models.TextField('Текст')
    
    # Поле для даты и времени публикации поста
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(  
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    
    # Связь с моделью пользователя - автор поста ---
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        null=True,  
    )
    
    # Связь с моделью Location - местоположение поста
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,   
        null=True,  
        verbose_name='Местоположение',
    )
    
    # Связь с моделью Category - категория поста
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False, 
        null=True,   
        verbose_name='Категория',
    ) #---
    
    # Поле для загрузки изображений к постам
    image = models.ImageField(
        'Изображение',
        upload_to='post_images',  # Папка для загрузки изображений
        blank=True,  # Изображение не обязательно
    )


    class Meta:
        # Настройки отображения модели в админке
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        
        ordering = ('-pub_date',) # Сортировка по убыванию (сначала новые посты) (убрать минус)
        
        # Имя обратной связи для связанных моделей
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:SYMBOL_CONSTRAINT]



class Comment(PublishedModel): #---
    """
    Модель для хранения комментариев к постам.
    Пользователи могут комментировать посты.
    """
    
    # Поле для текста комментария
    text = models.TextField('Комментарий')
    
    # Связь с моделью Post - пост, к которому относится комментарий ---
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    
    # Связь с моделью User - автор комментария
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )#---


    class Meta:
        # Сортировка комментариев: по дате
        ordering = ('created_at',)
        
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        
        # Имя обратной связи для связанных моделей
        default_related_name = 'comments'

    def __str__(self):
        """
        Строковое представление объекта для удобного отображения.
        Возвращает информацию о посте, авторе и первые 20 символов текста.
        """
        return (f'Пост {self.pk}, комментарий от пользователя {self.author}, '
                f'текст: {self.text[:LIMIT_FOR_COMMENT_TITLE]}')