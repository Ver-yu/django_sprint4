from django.urls import include, path

from blog import views

# Определяем пространство имен для URL этого приложения
app_name = 'blog'


# Группа URL-адресов для работы с постами и комментариями
posts_urls = [
    # Детальное отображение конкретного поста по его ID
    path(
        '<int:pk>/', 
        views.PostDetailView.as_view(),  
        name='post_detail' 
    ),
    
    # Создание нового поста (доступно только авторизованным пользователям)
    path(
        'create/',
        views.PostCreateView.as_view(), 
        name='create_post' 
    ),
    
    # Редактирование существующего поста (только для автора поста)
    path(
        '<int:post_id>/edit/', 
        views.PostUpdateView.as_view(), 
        name='edit_post' 
    ),
    
    # Удаление поста (только для автора поста)
    path(
        '<int:post_id>/delete/',  
        views.PostDeleteView.as_view(), 
        name='delete_post' 
    ),
    
    # Добавление комментария к посту (доступно только авторизованным)
    path(
        '<int:post_id>/comment/', 
        views.CommentCreateView.as_view(), 
        name='add_comment'
    ),
    
    # Редактирование существующего комментария (только для автора комментария)
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/', 
        views.CommentUpdateView.as_view(),  
        name='edit_comment'
    ),
    
    # Удаление комментария (только для автора комментария)
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/', 
        views.CommentDeleteView.as_view(), 
        name='delete_comment',  
    ),
]


# Группа URL-адресов для работы с профилями пользователей
profile_urls = [
    # Редактирование профиля текущего пользователя
    path(
        'edit/',
        views.ProfileUpdateView.as_view(), 
        name='edit_profile' 
    ),
    
    # Просмотр профиля любого пользователя по его username
    path(
        '<str:username>/', 
        views.ProfileView.as_view(), 
        name='profile'
    ),
]


# Основной список URL-адресов приложения blog
urlpatterns = [
    # Главная страница блога (список всех опубликованных постов)
    path(
        '',
        views.IndexHome.as_view(),  
        name='index'
    ),
    
    # Подключение всех маршрутов для работы с постами
    path('posts/', include(posts_urls)),
    
    # Подключение всех маршрутов для работы с профилями
    path('profile/', include(profile_urls)),
    
    # Отображение постов конкретной категории по её slug (человекочитаемый идентификатор)
    path(
        'category/<slug:category_slug>/', 
        views.CategoryListView.as_view(),  
        name='category_posts' 
    )
]