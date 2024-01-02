from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from clients.forms import ClientForm
from clients.models import Client


class ClientListView(LoginRequiredMixin, ListView):
    """
    Контроллер, который отвечает за просмотр всех клиентов
    """
    model = Client
    extra_content = {
        'title': 'Список клиентов'
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset


class ClientDetailView(LoginRequiredMixin, DetailView):
    """
    Контроллер, который отвечает за просмотр клиента
    """
    model = Client

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['title'] = client.email
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """
    Контроллер, который отвечает за создание клиента
    """
    model = Client
    form_class = ClientForm
    extra_context = {
        'title': 'Добавить клиентв'
    }

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('clients:client_detail', args=[self.object.pk])


class ClientUpdateView(UpdateView):
    """
    Контроллер, который отвечает за изменение клиента
    """
    model = Client
    form_class = ClientForm
    extra_context = {
        'title': 'Изменить клиента'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object

    def get_success_url(self):
        return reverse('clients:client_detail', args=[self.object.pk])


class ClientDeleteView(DeleteView):
    """
    Контроллер, который отвечает за удаление клиента
    """
    model = Client
    success_url = reverse_lazy('clients:client_list')
    extra_context = {
        'title': 'Удалить клиента'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object
