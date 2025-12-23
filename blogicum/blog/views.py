from django.contrib.auth.mixins import LoginRequiredMixin  # Для ограничения доступа авторизованным пользователям

from django.shortcuts import get_object_or_404  # Для безопасного получения объектов или возврата 404

from django.urls import reverse  # Для генерации URL по имени маршрута

from .utils import published_only  # Утилита для фильтрации опубликованных постов

from django.utils import timezone  # Для работы с датами и временем

from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)  

from blog.forms import CommentForm, PostForm, UserForm 

from blog.mixins import CommentChangeMixin, CustomListMixin, PostChangeMixin 

from blog.models import Category, Comment, Post, User  



class IndexHome(CustomListMixin, ListView):
    """Контроллер для отображения главной страницы блога."""
    
    # Указываем шаблон, который будет использоваться для рендеринга
    template_name = 'blog/index.html'

    def get_queryset(self):
        """
        Возвращает QuerySet постов для главной страницы.
        Использует объединенную функцию для получения только опубликованных постов.
        """
        # Импортируем функцию внутри метода для избежания циклических импортов
        from .utils import get_posts_with_comments
        # Получаем только опубликованные посты для всех пользователей
        return get_posts_with_comments(show_all=False)




class ProfileView(CustomListMixin, ListView): #--- 7 12
    """Контроллер для отображения профиля пользователя."""
    
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs): 
        """
        Добавляет информацию о профиле в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self): # --- 7 12
        """
        Возвращает QuerySet постов пользователя.
        Автор видит все свои посты, другие пользователи - только опубликованные.
        """
        # Получаем пользователя по username
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        
        # Получаем базовый QuerySet с аннотацией комментариев
        base_qs = super().get_queryset()
        
        # Фильтруем по автору
        author_qs = base_qs.filter(author=self.author)
        
        # Применяем фильтрацию опубликованных (если пользователь не автор)
        if self.author != self.request.user:
            from .utils import published_only
            return published_only(author_qs)
        
        # Автор видит все свои посты (включая неопубликованные)
        return author_qs



class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер для редактирования профиля текущего пользователя."""
    
    model = User  # Модель пользователя
    form_class = UserForm  # Форма для редактирования профиля
    template_name = 'blog/user.html'  # Шаблон формы

    def get_object(self, queryset=None):
        """
        Возвращает объект текущего пользователя для редактирования.
        """
        return self.request.user

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного редактирования.
        """
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )



class CategoryListView(CustomListMixin, ListView): # --- 7
    """Контроллер для отображения постов в конкретной категории."""
    
    template_name = 'blog/category.html'

    def get_queryset(self): # ---7
        """
        Возвращает QuerySet постов определенной категории.
        Проверяет, что категория существует и опубликована.
        """
        # Получаем категорию по slug, проверяя что она опубликована
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        
        # Получаем базовый QuerySet с аннотацией комментариев из миксина
        base_qs = super().get_queryset()
        
        # Фильтруем по категории
        filtered_qs = base_qs.filter(category__slug=self.kwargs['category_slug'])
        
        # Применяем фильтрацию опубликованных постов
        from .utils import published_only
        return published_only(filtered_qs)

    def get_context_data(self, **kwargs):
        """
        Добавляет объект категории в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView): #--- 6 14
    """Контроллер для создания нового поста."""
    
    model = Post  # Модель поста --- 14
    form_class = PostForm  # Форма для создания поста 
    template_name = 'blog/create.html'  # Шаблон формы ---14

    def form_valid(self, form):
        """
        Обрабатывает валидную форму, устанавливая автора поста.
        """
        # Автоматически устанавливаем текущего пользователя как автора поста
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str: #--- 6
        """
        Возвращает URL для перенаправления после успешного создания поста.
        """
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )#---



class PostUpdateView(LoginRequiredMixin, PostChangeMixin, UpdateView):
    """Контроллер для редактирования существующего поста."""
    
    form_class = PostForm  # Форма для редактирования поста

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного редактирования.
        """
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])



class PostDeleteView(LoginRequiredMixin, PostChangeMixin, DeleteView):
    """Контроллер для удаления поста."""
    
    def get_context_data(self, **kwargs):
        """
        Добавляет форму с данными поста в контекст для отображения в шаблоне подтверждения.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления поста.
        """
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )



class PostDetailView(DetailView): # --- 16 2.5 2.6
    """
    Контроллер для детального просмотра поста.
    Реализует проверку прав доступа: только автор может видеть неопубликованные посты.
    """
    
    model = Post  # Модель поста
    template_name = 'blog/detail.html'  # Шаблон детального просмотра
    pk_url_kwarg = 'pk'  # Имя параметра в URL, содержащего ID поста

    def get_object(self, queryset=None): # --- 16 2.5
        """
        Возвращает объект поста с проверкой прав доступа.
        """
        # Первый вызов - проверка существования поста
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
    
        # Второй вызов - проверка доступности для текущего пользователя
        if post.author != self.request.user:
            # Если пользователь не автор, проверяем опубликован ли пост
            post = get_object_or_404(
                published_only(Post.objects.all()),
                pk=self.kwargs['pk']
            )
        return post

    def get_context_data(self, **kwargs): # --- 2.6
        """
        Добавляет форму для комментария и список комментариев в контекст.
        """
        context = super().get_context_data(**kwargs)
        # Форма для добавления нового комментария
        context['form'] = CommentForm()
        # Список комментариев к посту с оптимизацией запросов
        context['comments'] = (
            self.object.comments.select_related('author') # Использование поля связи
        )
        return context



class CommentCreateView(LoginRequiredMixin, CreateView): # ---14
    """Контроллер для создания нового комментария."""
    
    model = Comment  # Модель комментария
    form_class = CommentForm  # Форма для комментария
    pk_url_kwarg = 'post_id'  # Имя параметра с ID поста в URL --- 14

    def form_valid(self, form):
        """
        Обрабатывает валидную форму, устанавливая автора и пост для комментария.
        """
        # Устанавливаем текущего пользователя как автора комментария
        form.instance.author = self.request.user
        # Находим пост по ID из URL и привязываем к комментарию
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Возвращает URL для перенаправления после успешного создания комментария.
        """
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('post_id')})



class CommentUpdateView(LoginRequiredMixin, CommentChangeMixin, UpdateView):
    """Контроллер для редактирования существующего комментария."""
    
    form_class = CommentForm  # Форма для редактирования комментария



class CommentDeleteView(LoginRequiredMixin, CommentChangeMixin, DeleteView):
    """Контроллер для удаления комментария."""
    
    # Наследует все необходимые методы из CommentChangeMixin