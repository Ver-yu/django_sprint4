from django.contrib import admin

from blog.models import Category, Comment, Location, Post

# Стандартный класс для админки пользователей
from django.contrib.auth.admin import UserAdmin

# Функция для получения модели пользователя (стандартной или кастомной)
from django.contrib.auth import get_user_model

# Константа для текста описания
TEXT = 'Описание публикации.'


# Регистрация модели Post с кастомным админ-классом
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления постами (публикациями).
    """
    
    # Поля, которые будут отображаться в списке записей
    list_display = (
        'title',       
        'text',         
        'is_published',  
        'category',     
        'location',    
        'created_at',  
        'image',       
    )
    

    # Поля, которые можно редактировать прямо из списка без перехода в форму
    list_editable = (
        'is_published',  
        'category',      
        'location',     
    )
    

    # Поля, по которым работает поиск (появляется строка поиска вверху)
    search_fields = ('title',)  
    
    
    # Поля для фильтрации списка (появляется боковая панель фильтров)
    list_filter = ('category',) 
    

    # Поля, которые являются ссылками на редактирование записи
    list_display_links = ('title',) 
    

    # Группировка полей в форме редактирования с описаниями
    fieldsets = (
        # Первый блок "Блок-1" с основными полями
        ('Блок-1', {
            'fields': ('title', 'author', 'is_published',),
            'description': '%s' % TEXT, 
        }),

        # Второй блок "Доп. информация" с дополнительными полями
        ('Доп. информация', {
            'classes': ('wide', 'extrapretty'), 
            'fields': ('text', 'category', 'location', 'pub_date', 'image',),
        }),
    )



# Встроенная форма для отображения постов внутри других моделей
class PostInline(admin.TabularInline):
    """
    Встроенное отображение постов внутри форм других моделей.
    Полезно для просмотра всех постов категории/локации на одной странице.
    """
    model = Post      
    extra = 0           



# Регистрация модели Category с кастомным админ-классом
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления категориями.
    """
    
    # Встраиваем отображение постов в форму категории
    inlines = (
        PostInline,    
    )
    

    # Поля для отображения в списке категорий
    list_display = (
        'title',       
        'slug',          
        'is_published',  
        'description',  
        'created_at',    
    )
    

    # Фильтрация списка категорий
    list_filter = ('title',)  



# Регистрация модели Location с кастомным админ-классом
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления местоположениями.
    """
    
    # Встраиваем отображение постов в форму местоположения
    inlines = (
        PostInline,      
    )
    
    # Поля для отображения в списке местоположений
    list_display = (
        'name',         
        'is_published',  
    )
    
    # Фильтрация списка местоположений
    list_filter = ('name',) 



# Регистрация модели Comment с кастомным админ-классом
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления комментариями.
    """
    
    # Поля для отображения в списке комментариев
    list_display = (
        'text',         
        'author',       
        'is_published', 
        'created_at',    
    )
    
    # Фильтрация списка комментариев
    list_filter = ('author',) 
    
    # Поля, редактируемые прямо из списка
    list_editable = ('is_published',) 



# Получаем модель пользователя (стандартную User или кастомную, если она определена)
User = get_user_model()


# Разрегистрируем стандартную модель пользователя (если она была зарегистрирована)
admin.site.unregister(User)


# Регистрируем модель пользователя с кастомным админ-классом
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомизированный админ-класс для управления пользователями.
    Наследуется от стандартного UserAdmin для сохранения безопасности работы с паролями.
    """
    
    # Поля, которые будут отображаться в списке пользователей
    list_display = (
        'username',     
        'email',       
        'first_name',  
        'last_name',   
        'is_staff',     
        'is_active',   
    )
    
    # Поля для фильтрации списка пользователей
    list_filter = (
        'is_staff',     
        'is_superuser', 
        'is_active',   
        'groups',      
    )
    
    # Поля, по которым работает поиск пользователей
    search_fields = (
        'username',    
        'first_name',    
        'last_name',   
        'email',      
    )
    
    # Группировка полей в форме редактирования пользователя
    fieldsets = (
        # Блок "Основная информация" (логин и пароль)
        (None, {
            'fields': ('username', 'password') 
        }),
        # Блок "Персональная информация"
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        # Блок "Права доступа" 
        ('Права доступа', {
            'fields': (
                'is_active',          
                'is_staff',           
                'is_superuser',      
                'groups',              
                'user_permissions',   
            ),
        }),
        # Блок "Важные даты" (только для чтения)
        ('Важные даты', {
            'fields': ('last_login', 'date_joined'),  # Автоматически заполняемые поля
        }),
    )
    
    # Настройки для формы ДОБАВЛЕНИЯ нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),      # CSS-классы для оформления
            'fields': ('username', 'password1', 'password2'),  # Поля при создании
        }),
    )