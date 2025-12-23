
## Пошаговая инструкция по запуску

**Создание виртуального окружения**
python -m venv venv

**Активация виртуального окружения**
venv\Scripts\activate

**Обновление pip и установка зависимостей**
python -m pip install --upgrade pip
pip install -r requirements.txt

**Переход в директорию проекта и выполнение миграций**
cd blogicum
python manage.py migrate

**Загрузка тестовых данных**
python manage.py loaddata db.json

**Запуск сервера разработки**
python manage.py runserver

**Открытие в браузере**
По адресу: http://127.0.0.1:8000/

Дополнительные команды для работы с проектом
**Создание суперпользователя (администратора)**
python manage.py createsuperuser

**Показать все миграции и их статус**
python manage.py showmigrations

**Создание миграций после изменения моделей**
python manage.py makemigrations

**Применение конкретной миграции**
python manage.py migrate blog 0001_initial

**Сбор статических файлов (для production)**
python manage.py collectstatic



## Отчет по проекту "Блогикум"


### Раздел 1

#### 1. Модели Category, Location, Post, Comment представлены в админке

Файл: blogicum/blog/admin.py

```python
from django.contrib import admin
from blog.models import Category, Comment, Location, Post
# ... другие импорты ...

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления постами (публикациями).
    """
    list_display = ('title', 'text', 'is_published', 'category', 'location', 'created_at', 'image')
    list_editable = ('is_published', 'category', 'location')
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    fieldsets = (
        ('Блок-1', {'fields': ('title', 'author', 'is_published'), 'description': '%s' % TEXT}),
        ('Доп. информация', {'classes': ('wide', 'extrapretty'), 'fields': ('text', 'category', 'location', 'pub_date', 'image')}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления категориями.
    """
    inlines = (PostInline,)
    list_display = ('title', 'slug', 'is_published', 'description', 'created_at')
    list_filter = ('title',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления местоположениями.
    """
    inlines = (PostInline,)
    list_display = ('name', 'is_published')
    list_filter = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления комментариями.
    """
    list_display = ('text', 'author', 'is_published', 'created_at')
    list_filter = ('author',)
    list_editable = ('is_published',)
```

Все четыре модели проекта зарегистрированы в административном интерфейсе Django с использованием декоратора @admin.register(). Каждая модель имеет свой класс администратора с настройками отображения, фильтрации и поиска, что позволяет администраторам управлять данными через удобный веб-интерфейс без необходимости прямого доступа к базе данных.





#### 2. Настройка параметров on_delete для ForeignKey полей
Файл: blogicum/blog/models.py

```python
from django.contrib.auth import get_user_model
from django.db import models
from core.models import PublishedModel

User = get_user_model()

class Post(PublishedModel):
    """
    Основная модель для хранения публикаций (постов) в блоге.
    Содержит основной контент блога.
    """
    # ... другие поля ...

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Удаление постов при удалении автора
        verbose_name='Автор публикации',
        null=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,  # Установка NULL при удалении локации
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # Установка NULL при удалении категории
        blank=False,
        null=True,
        verbose_name='Категория',
    )
    # ... другие поля ...


class Comment(PublishedModel):
    """
    Модель для хранения комментариев к постам.
    Пользователи могут комментировать посты.
    """
    # ... другие поля ...
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # Удаление комментариев при удалении поста
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Удаление комментариев при удалении пользователя
    )
    # ... другие поля ...

```

Для обеспечения целостности данных все связи типа ForeignKey имеют явно заданный параметр on_delete. Для большинства связей используется CASCADE (каскадное удаление), но для location и category в модели Post применен SET_NULL, что позволяет сохранить посты даже при удалении связанных локаций или категорий. Это предотвращает нежелательное каскадное удаление данных.





#### 3. Форма для постов с редактируемыми полями is_published и pub_date
Файл: blogicum/blog/forms.py

```python
from django import forms
from blog.models import Comment, Post, User

class PostForm(forms.ModelForm):
    """
    Форма для работы с постами (публикациями).
    """
    class Meta:
        model = Post
        exclude = ('author',)  # Автор устанавливается автоматически
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}  # Современный виджет выбора даты
            )
        }
```

Форма PostForm включает поля is_published и pub_date, что позволяет авторам управлять публикацией своих постов. Поле pub_date использует HTML5-виджет datetime-local для удобного выбора даты и времени, а поле is_published дает возможность быстро публиковать или скрывать посты. Поле author исключено из формы, так как оно устанавливается автоматически в представлении на основе текущего пользователя.





#### 4. Содержательные имена параметров в URL
Файл: blogicum/blog/urls.py

```python
from django.urls import include, path
from blog import views

app_name = 'blog'

posts_urls = [
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('<int:post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
]

urlpatterns = [
    path('', views.IndexHome.as_view(), name='index'),
    path('posts/', include(posts_urls)),
    # ... другие маршруты ...
]
```

Вместо абстрактных имен параметров pk или id используются содержательные имена post_id и comment_id. Это делает URL-адреса более понятными и документирует, к какому типу объекта относится каждый параметр. Например, /posts/123/edit/ явно указывает, что редактируется пост с ID 123.





#### 5. Корректный тип параметра для имени пользователя
Файл: blogicum/blog/urls.py

```python
profile_urls = [
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),  # Используется str, а не slug
]
```

Для параметра имени пользователя используется тип str, а не slug. Это важно, так как slug имеет ограничения (только латиница, цифры, дефис и подчеркивание), в то время как имена пользователей могут содержать различные символы и поддерживать разные языки. Тип str обеспечивает большую гибкость.





#### 6. Использование именованных маршрутов вместо явных URL
Файл: blogicum/blog/views.py и mixins.py 

```python
from django.urls import reverse
from django.shortcuts import redirect

class PostCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания нового поста."""
    def get_success_url(self) -> str:
        """
        Возвращает URL для перенаправления после успешного создания поста.
        """
        return reverse('blog:profile', kwargs={'username': self.request.user})

class PostChangeMixin:
    """
    Миксин для представлений изменения постов (редактирование, удаление).
    """
    def dispatch(self, request, *args, **kwargs): #Переопределяем метод dispatch для проверки прав доступа.
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
Файл: blogicum/templates/includes/post_card.html

html
<a href="{% url 'blog:post_detail' post.id %}" class="card-link">Читать полный текст</a>
<a class="text-muted" href="{% url 'blog:profile' post.author %}">@{{ post.author.username }}</a>
```

Во всем проекте URL-адреса формируются через имена маршрутов с использованием reverse() в представлениях и {% url %} в шаблонах. Это обеспечивает гибкость: при изменении структуры URL достаточно обновить только файл urls.py, не затрагивая остальной код. Также это делает код более читаемым и поддерживаемым.





#### 7. Извлечение объектов через get_object_or_404()
Файл: blogicum/blog/views.py

```python
from django.shortcuts import get_object_or_404

class ProfileView(CustomListMixin, ListView):
    """Контроллер для отображения профиля пользователя."""
    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        # ... дальнейшая обработка ...

class CategoryListView(CustomListMixin, ListView):
    """Контроллер для отображения постов в конкретной категории."""
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        # ... дальнейшая обработка ...

```

Функция get_object_or_404() используется для безопасного извлечения объектов из базы данных. Она автоматически выбрасывает исключение Http404, если объект не найден, что избавляет от необходимости вручную проверять существование объекта и корректно обрабатывает ситуацию отсутствия объекта, возвращая стандартную страницу 404.





#### 8. Дополнение постов количеством комментариев
Файл: blogicum/blog/mixins.py

```python
from django.db.models import Count

class CustomListMixin:
    """ Предоставляет общую логику для отображения списка постов:"""
    model = Post
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments')  # Аннотация количества комментариев
        )
        return queryset.order_by(*Post._meta.ordering)
```

Все посты на главной странице, в категориях и профилях дополняются информацией о количестве комментариев через метод annotate() с использованием агрегатной функции Count(). Это позволяет отображать эту информацию без дополнительных запросов к базе данных, решая проблему N+1 запросов.





#### 9. Централизованное вычисление количества комментариев
Файл: blogicum/blog/utils.py

```python
from django.db.models import Count
from .models import Post

def get_posts_with_comments(show_all=False, queryset=None):
    """    Возвращает QuerySet постов с оптимизацией запросов и подсчетом комментариев."""
    if queryset is None:
        queryset = Post.objects.all()
    
    queryset = queryset.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')  # Подсчет комментариев в одном месте
    )
    
    return queryset.order_by(*Post._meta.ordering)
```

Логика подсчета комментариев централизована в функции get_posts_with_comments(), что исключает дублирование кода и обеспечивает согласованность во всем проекте. Использование annotate() делает подсчет эффективным, добавляя поле comment_count к каждому объекту поста в QuerySet.





#### 10. Сортировка после применения annotate()
Файл: blogicum/blog/mixins.py

```python
class CustomListMixin:
    """Предоставляет общую логику для отображения списка постов"""
    def get_queryset(self):
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments')
        )
        return queryset.order_by(*Post._meta.ordering)  # Явная сортировка
```

После применения annotate() необходимо явно указать сортировку через order_by(), так как автоматическая сортировка из модели становится недоступной. Использование *Post._meta.ordering обеспечивает применение сортировки, заданной в мета-классе модели. Без сортировки пагинация будет работать некорректно.





#### 11. Функция для создания пагинированных страниц
Файл: blogicum/blog/utils.py

```python
from django.core.paginator import Paginator

def get_paginated_page(queryset, request, per_page=10):
    """Создает пагинацию для QuerySet. Разбивает большой список объектов на страницы для удобного отображения."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
```

Функция get_paginated_page() централизует логику создания пагинированных страниц, обеспечивая единообразие и упрощая поддержку кода. Она принимает QuerySet, объект запроса и количество элементов на странице, возвращая объект страницы. Это избавляет от дублирования кода пагинации в разных представлениях.





#### 12. Различный доступ к постам в зависимости от посетителя
Файл: blogicum/blog/views.py

```python
class ProfileView(CustomListMixin, ListView):
    def get_queryset(self):
        """
        Возвращает QuerySet постов пользователя.
        Автор видит все свои посты, другие пользователи - только опубликованные.
        """
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        
        # Получаем базовый QuerySet с аннотацией комментариев
        base_qs = super().get_queryset()
        
        # Фильтруем по автору
        author_qs = base_qs.filter(author=self.author)
        
        # Применяем фильтрацию (если пользователь не автор)
        if self.author != self.request.user:
            from .utils import published_only
            return published_only(author_qs)
        
        return author_qs  # Автор видит все свои посты (включая аннотацию)
```

На странице профиля реализована дифференцированная логика отображения постов. Автор видит все свои посты (включая неопубликованные), а другие пользователи — только опубликованные посты. Это обеспечивает приватность черновиков и соответствует принципу наименьших привилегий.





#### 13. Централизованная фильтрация опубликованных постов
Файл: blogicum/blog/utils.py

```python
from django.utils import timezone
from .models import Post

def published_only(queryset=None):
    """Фильтрует QuerySet, оставляя только опубликованные посты."""
    if queryset is None:
        from .models import Post
        queryset = Post.objects.all()
    
    return queryset.filter(
        is_published=True,              # Пост опубликован
        pub_date__lte=timezone.now(),   # Дата публикации не в будущем
        category__is_published=True     # Категория тоже опубликована
    )
```

Функция published_only() централизует логику фильтрации опубликованных постов, учитывая три критерия: статус публикации поста, дату публикации (не должна быть в будущем) и статус категории (должна быть опубликована). Это обеспечивает единообразие фильтрации во всем проекте и упрощает поддержку.





#### 14. Защита представлений от неавторизованного доступа
Файл: blogicum/blog/views.py

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class PostCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания нового поста."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    # ... другие методы ...

class CommentCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания нового комментария."""
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    # ... другие методы ...
```

Все представления для создания, редактирования и удаления постов и комментариев защищены миксином LoginRequiredMixin, который автоматически перенаправляет неавторизованных пользователей на страницу входа при попытке доступа к защищенным действиям. Это эквивалент декоратора @login_required для классов-представлений.





#### 15. Использование redirect() с именами маршрутов
Файл: blogicum/blog/mixins.py

```python
from django.shortcuts import redirect

class PostChangeMixin:
    """Миксин для представлений изменения постов (редактирование, удаление)."""
    def dispatch(self, request, *args, **kwargs):
        """Переопределяем метод dispatch для проверки прав доступа."""
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
```

Функция redirect() может принимать имена маршрутов напрямую, без необходимости предварительного вычисления URL через reverse(). Это делает код более простым и читаемым. Например, redirect('blog:post_detail', post_id=123) автоматически сгенерирует правильный URL на основе конфигурации в urls.py.





#### 16. Проверка авторства при просмотре поста
Файл: blogicum/blog/views.py

```python
from django.shortcuts import get_object_or_404
from .utils import published_only

class PostDetailView(DetailView):
    """
    Контроллер для детального просмотра поста.
    Реализует проверку прав доступа: только автор может видеть неопубликованные посты.
    """
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """Возвращает объект поста с проверкой прав доступа."""
        # Первый вызов - проверка существования
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
    
        # Второй вызов - проверка доступности
        if post.author != self.request.user:
            post = get_object_or_404(
                published_only(Post.objects.all()),
                pk=self.kwargs['pk']
            )
        return post
```

В представлении детального просмотра поста реализована двухэтапная проверка. Сначала пост извлекается для проверки авторства, затем, если пользователь не является автором, выполняется повторный запрос с фильтрацией по опубликованности через функцию published_only(). Это гарантирует, что только автор может видеть свои неопубликованные посты, а другим пользователям показываются только опубликованные записи.








### Раздел 2

#### 1. Исключение служебных папок из репозитория
static, static-dev и html. 



#### 2. Использование exclude в форме для поста
Файл: blogicum/blog/forms.py

```python
class PostForm(forms.ModelForm):
    """
    Форма для работы с постами (публикациями).
    Наследуется от ModelForm для автоматического создания полей на основе модели.
    """
    class Meta:
        model = Post
        exclude = ('author',)  # Автор исключается, так как устанавливается автоматически
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }
```

Форма для поста настроена через exclude, а не через fields, что автоматически включает все поля модели, кроме указанных. Поле created_at не редактируемое (имеет auto_now_add=True в модели), поэтому Django автоматически исключает его из формы, что соответствует требованиям. Это более удобный подход, когда нужно включить большинство полей модели.





#### 3. Объединенная функция фильтрации и дополнения комментариев
Файл: blogicum/blog/utils.py

```python
def get_posts_with_comments(show_all=False, queryset=None):
    """
    Возвращает QuerySet постов с оптимизацией запросов и подсчетом комментариев.
    """
    if queryset is None:
        queryset = Post.objects.all()
    
    if not show_all:  # Параметр для управления фильтрацией
        queryset = published_only(queryset)
    
    queryset = queryset.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')
    )
    
    return queryset.order_by(*Post._meta.ordering)
```

Функция get_posts_with_comments() объединяет фильтрацию опубликованных постов и дополнение количеством комментариев. Параметр show_all позволяет гибко управлять фильтрацией: для автора, просматривающего свой профиль, можно показать все посты (show_all=True), а для других пользователей — только опубликованные (show_all=False). Это уменьшает дублирование кода.





#### 4. Параметр по умолчанию для функции фильтрации
Файл: blogicum/blog/utils.py

```python
def published_only(queryset=None):  # Параметр с значением по умолчанию
    """ Фильтрует QuerySet, оставляя только опубликованные посты."""
    if queryset is None:
        from .models import Post
        queryset = Post.objects.all()  # Если не передан, берем все посты
    
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
```

Функция published_only() принимает необязательный параметр queryset со значением по умолчанию None. Это позволяет использовать функцию как с конкретным набором постов, так и без него. Если параметр не передан, функция работает со всеми постами в базе данных. Это делает функцию более гибкой и удобной для использования в разных контекстах.





#### 5. Двухэтапная проверка в PostDetailView
Файл: blogicum/blog/views.py

```python
class PostDetailView(DetailView):
    """Контроллер для детального просмотра поста."""
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """Возвращает объект поста с проверкой прав доступа."""
        # Первый вызов - проверка существования
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
    
        # Второй вызов - проверка доступности
        if post.author != self.request.user:
            post = get_object_or_404(
                published_only(Post.objects.all()),
                pk=self.kwargs['pk']
            )
        return post
```

В представлении детального просмотра поста используется рекомендуемый подход с двумя вызовами get_object_or_404(). Первый вызов извлекает пост из полной таблицы для проверки существования и авторства. Второй вызов выполняется только если пользователь не является автором и проверяет, опубликован ли пост. Это обеспечивает правильную логику доступа к постам.





#### 6. Использование полей связи для доступа к связанным объектам
Файл: blogicum/blog/views.py

```python
class PostDetailView(DetailView):
    def get_context_data(self, **kwargs):
        """Добавляет форму для комментария и список комментариев в контекст."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')  # Использование поля связи
        )
        return context
```

Вместо прямых запросов к базе данных (Post.objects.filter(category=category)) используются поля связи через related_name. В модели Comment установлен default_related_name = 'comments', поэтому к комментариям поста можно обращаться как post.comments. Это не только более эффективно (меньше запросов к БД), но и является единственным возможным способом в шаблонах, где нельзя вызывать методы с параметрами.





#### 7. Сортировка через *Post._meta.ordering
Файл: blogicum/blog/mixins.py

```python
class CustomListMixin:
    """Миксин для списковых представлений (ListView)."""
    def get_queryset(self):
        """Возвращает оптимизированный QuerySet постов."""
        queryset = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments')
        )
        return queryset.order_by(*Post._meta.ordering) # Сортируем посты согласно настройкам в модели Post
```

После применения annotate() сортировка устанавливается через *Post._meta.ordering, что гарантирует совпадение сортировки с настройками модели. Использование распаковки (*) позволяет применить все поля сортировки, указанные в Meta-классе модели Post. Это более надежный подход, чем явное указание полей сортировки, так как автоматически адаптируется к изменениям в модели.





#### 8. Обработка GET и POST запросов в формах
В проекте используются классы-представления Django (CreateView, UpdateView), которые автоматически обрабатывают GET и POST запросы. Однако если бы использовались функции-представления, можно было бы применить рекомендуемый подход:

```python
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    
    if not form.is_valid():  # Работает для GET и невалидного POST
        return render(request, 'blog/create.html', {'form': form})
    
    # Код для валидного POST-запроса
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:profile', username=request.user.username)
```

Это позволяет избежать явной проверки if request.method == 'POST': и упрощает код.





#### 9. Безопасная админка для модели пользователя
Файл: blogicum/blog/admin.py

```python
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

# Разименуем стандартную регистрацию
admin.site.unregister(User)

# Регистрируем с кастомным админом
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомизированный админ-класс для пользователей.
    UserAdmin скрывает пароли и предоставляет безопасный интерфейс.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
```

Для модели пользователя используется специальный админ-класс UserAdmin, который правильно обрабатывает секретные поля (пароли). В отличие от ModelAdmin, UserAdmin скрывает хэши паролей в интерфейсе и предоставляет безопасные формы для создания и изменения пользователей. Это предотвращает случайное раскрытие чувствительной информации.