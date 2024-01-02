from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from pytils.translit import slugify

from blog.forms import BlogForm
from blog.models import Post


class BlogCreateView(CreateView):
    """
    Контроллер, который отвечает за создание публикации
    """
    model = Post
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')
    extra_context = {
        'title': 'Создать публикацию'
    }

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.title)
            new_mat.save()

        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    """
    Контроллер, который отвечает за измененме публикации
    """
    model = Post
    form_class = BlogForm
    extra_context = {
        'title': 'Изменить публикцию'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object

    def form_valid(self, form):
        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.title)
            new_mat.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:blog_detail', args=[self.object.pk])


class BlogListView(ListView):
    """
    Контроллер, который отвечает за просмотр всех публикаций
    """
    model = Post
    extra_context = {
        'title': 'Blog'
    }

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff or user.is_superuser:
                queryset = super().get_queryset().order_by('pk')

            else:
                queryset_1 = super().get_queryset().filter(owner=user).order_by('pk')
                queryset_2 = super().get_queryset().filter(is_published=True, is_active=True).order_by('pk')
                queryset = queryset_2.union(queryset_1)

        else:
            queryset = super().get_queryset().filter(
                is_published=True).order_by('-pk')
        return queryset


class BlogDetailView(DetailView):
    """
    Контроллер, который отвечает за просмотр публикации
    """
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        post.views_count += 1
        post.save()
        context['title'] = post.title
        return context


class BlogDeleteView(DeleteView):
    """
    Контроллер, который отвечает за удаление публикации
    """
    model = Post
    success_url = reverse_lazy('blog:blog_list')
    extra_context = {
        'title': 'Удалить публикацию'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object
