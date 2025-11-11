from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

NUMBER_OF_POSTS = 10


class AuthorView(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostView(AuthorView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail',
                        self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CommentView(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class IndexListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_POSTS
    queryset = Post.objects.filter_posts_for_publication().count_comments()


class PostDetailView(ListView):
    template_name = 'blog/detail.html'
    paginate_by = NUMBER_OF_POSTS

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(Post.objects.filter_posts_for_publication(),
                                 pk=self.kwargs['post_id'])

    def get_queryset(self):
        return self.get_object().comments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = self.get_object()
        return context


class PostUpdateView(PostView, UpdateView):
    pass


class PostDeleteView(PostView, DeleteView):
    pass


class CommentCreateView(CommentView, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post.objects.filter_posts_for_publication(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentUpdateView(CommentView, AuthorView, UpdateView):
    pass


class CommentDeleteView(CommentView, AuthorView, DeleteView):
    pass


class CategoryDetailView(ListView):
    template_name = 'blog/category.html'
    paginate_by = NUMBER_OF_POSTS
    slug_url_kwarg = 'category_slug'

    def get_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs[self.slug_url_kwarg], is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context

    def get_queryset(self):
        return self.get_category().posts.filter_posts_for_publication()


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_POSTS
    slug_url_kwarg = 'username'

    def get_profile(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        author = self.get_profile()
        posts = author.posts.count_comments()
        if author == self.request.user:
            return posts
        return posts.filter_posts_for_publication()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'email')
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.kwargs[self.slug_url_kwarg]})
