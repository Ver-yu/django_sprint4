from django import forms

# Импортируем модели, на основе которых будут создаваться формы
from blog.models import Comment, Post, User


# Форма для создания и редактирования постов (публикаций) --- 3  2.2
class PostForm(forms.ModelForm):
    """
    Форма для работы с постами (публикациями).
    Наследуется от ModelForm для автоматического создания полей на основе модели.
    """
    
    # Вложенный класс Meta определяет конфигурацию формы
    class Meta:
        model = Post
        
        # Автор будет задаваться автоматически в представлении (view)
        exclude = ('author',)
        
        # Кастомизация виджетов (элементов HTML) для полей формы
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


# Форма для создания и редактирования комментариев
class CommentForm(forms.ModelForm):
    """
    Форма для работы с комментариями.
    Наследуется от ModelForm для автоматического создания полей на основе модели.
    """
    
    # Вложенный класс Meta определяет конфигурацию формы
    class Meta:
        model = Comment
        
        fields = ('text',)
        
        # Кастомизация виджета для поля 'text'
        widgets = {
            'text': forms.Textarea(attrs={'cols': 10, 'rows': 10})
        }


# Форма для редактирования профиля пользователя
class UserForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Наследуется от ModelForm для автоматического создания полей на основе модели User.
    """
    
    class Meta:
        # Модель пользователя, на основе которой создается форма
        model = User
        
        # Поля, которые будут отображаться в форме редактирования профиля
        fields = ('username', 'first_name', 'last_name', 'email',)
