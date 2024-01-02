import calendar
import random
from datetime import timedelta, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, DetailView, UpdateView

from blog.models import Post
from clients.models import Client
from config import settings
from newsletter.forms import MessageForm, MailingSettingsForm
from newsletter.models import Message, MailingSettings, MailingLog


class MainPage(LoginRequiredMixin, TemplateView):
    """
    Контроллер главной страницы
    """
    login_url = 'users:login'
    template_name = 'newsletter/main_page.html'
    extra_context = {
        'title': 'Cервис рассылки сообщений'
    }

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        if self.request.method == 'GET':
            if settings.CACHE_ENABLED:
                key = f'cached_statistics'
                cached_context = cache.get(key)
                if cached_context is None:
                    context = super().get_context_data(*args, **kwargs)
                    if not user.is_staff:
                        context['mailing_count'] = MailingSettings.objects.filter(owner=user).count()
                        context['enabled_mailing'] = MailingSettings.objects.filter(owner=user).filter(
                            status='Запущена').count()
                        unic_client = []
                        for client in Client.objects.filter(owner=user):
                            unic_client.append(client.email)
                        context['unique_clients'] = len(set(unic_client))
                        all_blog_posts = Post.objects.all()
                        random.shuffle(list(all_blog_posts))
                        context['three_random_posts'] = all_blog_posts[:3]
                    else:
                        context['mailing_count'] = MailingSettings.objects.all().count()
                        context['enabled_mailing'] = MailingSettings.objects.all().filter(status='Запущена').count()
                        unic_client = []
                        for client in Client.objects.all():
                            unic_client.append(client.email)
                        context['unique_clients'] = len(set(unic_client))
                        main_page_context = {
                            'mailing_count': context['mailing_count'],
                            'enabled_mailing': context['enabled_mailing'],
                            'unique_clients': context['unique_clients']
                        }
                        cache.set(key, main_page_context)
                        all_blog_posts = Post.objects.all()
                        random.shuffle(list(all_blog_posts))
                        context['three_random_posts'] = all_blog_posts[:3]
                    return context
                else:
                    context = super().get_context_data(*args, **kwargs)
                    context['mailing_count'] = cached_context['mailing_count']
                    context['enabled_mailing'] = cached_context['enabled_mailing']
                    context['unique_clients'] = cached_context['unique_clients']
                    all_blog_posts = Post.objects.all()
                    random.shuffle(list(all_blog_posts))
                    context['three_random_posts'] = all_blog_posts[:3]
                return context


class MessageListView(LoginRequiredMixin, ListView):
    """
    Контроллер, который отвечает за просмотр всех сообщений
    """
    model = Message

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список Сообщений'
        return context_data


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Контроллер, который отвечает за создание сообщения
    """
    model = Message
    form_class = MessageForm
    extra_context = {
        'title': 'Создание сообщения'
    }

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('newsletter:message_list')


class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    Контроллер, который отвечает за просмотр сообщения
    """
    model = Message

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        message = self.get_object()
        context_data['title'] = message.title[:20]
        return context_data


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """
    Контроллер, который отвечает за изменение сообщения
    """
    model = Message
    form_class = MessageForm

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('newsletter:message_detail', args=[self.object.pk])


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """
    Контроллер, который отвечает за удаление сообщения
    """
    model = Message
    success_url = reverse_lazy('newsletter:message_list')
    extra_context = {
        'title': 'Удаление сообщения'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object


class MailingSettingsListView(LoginRequiredMixin, ListView):
    """
    Контроллер, который отвечает за просмотр всех рассылок
    """
    model = MailingSettings

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список рассылок'

        context_data['all'] = context_data['object_list'].count()
        context_data['active'] = context_data['object_list'].filter(status=MailingSettings.STARTED).count()
        context_data['completed'] = context_data['object_list'].filter(status=MailingSettings.COMPLETED).count()

        return context_data


def toggle_active(request, pk):
    if request.user.is_staff:
        distribution = MailingSettings.objects.get(pk=pk)
        distribution.is_active = not distribution.is_active
        distribution.save()
        return redirect('newsletter:mailing_settings_list')


class MailingSettingsCreateView(CreateView):
    """
    Контроллер, который отвечает за создание рассылки
    """
    model = MailingSettings
    form_class = MailingSettingsForm
    extra_context = {
        'title': 'Создание рассылки'
    }

    def get_initial(self):
        initial = super().get_initial()
        initial['owner'] = self.request.user
        return initial

    def form_valid(self, form):
        current_time = timezone.localtime(timezone.now())
        new_mailing = form.save()
        new_mailing.save()
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        if form.is_valid():
            clients = form.cleaned_data['clients']
            new_mailing = form.save()
            if new_mailing.start_time > current_time:
                new_mailing.next_newsletter = new_mailing.start_time
            else:
                if new_mailing.periodicity == "Раз в день":
                    new_mailing.next_newsletter = new_mailing.start_time + timedelta(days=1)

                if new_mailing.periodicity == "Раз в неделю":
                    new_mailing.next_newsletter = new_mailing.start_time + timedelta(days=7)

                if new_mailing.periodicity == "Раз в месяц":
                    today = datetime.today()
                    days = calendar.monthrange(today.year, today.month)[1]
                    new_mailing.next_newsletter = current_time + timedelta(days=days)

                for client in clients:
                    new_mailing.clients.add(client.pk)
                new_mailing.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('newsletter:mailing_settings_list')


class MailingSettingsDetailView(DetailView):
    """
    Контроллер, который отвечает за просмотр рассылки
    """
    model = MailingSettings

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = f'Детали рассылки:'
        return context_data


class MailingSettingsUpdateView(UpdateView):
    """
    Контроллер, который отвечает за изменение рассылки
    """
    model = MailingSettings
    form_class = MailingSettingsForm
    extra_context = {
        'title': 'Изменение рассылки'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object

    def get_initial(self):
        initial = super().get_initial()
        initial['owner'] = self.request.user
        return initial

    def form_valid(self, form):
        current_time = timezone.localtime(timezone.now())
        new_mailing = form.save()
        new_mailing.save()
        self.object = form.save()
        self.object.save()
        if form.is_valid():
            clients = form.cleaned_data['clients']
            new_mailing = form.save()
            if new_mailing.start_time > current_time:
                new_mailing.next_send = new_mailing.start_time
            else:
                if new_mailing.periodicity == "Раз в день":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=1)

                if new_mailing.periodicity == "Раз в неделю":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=7)

                if new_mailing.periodicity == "Раз в месяц":
                    today = datetime.today()
                    days = calendar.monthrange(today.year, today.month)[1]
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=days)

                for client in clients:
                    new_mailing.clients.add(client.pk)
                new_mailing.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('newsletter:mailing_settings_detail', args=[self.object.pk])


class MailingSettingsDeleteView(DeleteView):
    """
    Контроллер, который отвечает за удаление рассылки
    """
    model = MailingSettings

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object

    def get_success_url(self):
        return reverse('newsletter:mailing_settings_list')


class LogListView(LoginRequiredMixin, ListView):
    """
    Контроллер, который отвечает за просмотр логов
    """
    model = MailingLog
    template_name = 'newsletter/log_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список логов'

        context_data['all'] = context_data['object_list'].count()
        context_data['success'] = context_data['object_list'].filter(status=True).count()
        context_data['error'] = context_data['object_list'].filter(status=False).count()

        return context_data


class LogDetailView(LoginRequiredMixin, DetailView):
    """
    Контроллер, который отвечает за просмотр логов одной рассылки
    """
    model = MailingLog
    template_name = 'newsletter/log_detail.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        log = self.get_object()
        context_data['title'] = f'log: {log.pk}'
        return context_data


class LogDeleteView(LoginRequiredMixin, DeleteView):
    """
    Контроллер, который отвечает за удаление логов
    """
    model = MailingLog
    template_name = 'newsletter/log_confirm_delete.html'
    success_url = reverse_lazy('newsletter:log_list')
    extra_context = {
        'title': 'Удалить логи'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.groups.filter(name='Manager').exists():
                raise Http404
        return self.object
