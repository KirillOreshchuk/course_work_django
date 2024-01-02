from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetDoneView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, TemplateView

from config import settings
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User


class RegisterView(CreateView):
    """
    Контроллер, который отвечает регистрацию пользователя
    """
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()

        # создание токена и ссылки для подтверждения регистрации
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('users:confirm_email', kwargs={'uidb64': uid, 'token': token})

        current_site = '127.0.0.1:8000'

        send_mail(
            subject='Регистрация на платформе',
            message=f"Завершите регистрацию, перейдя по ссылке: http://{current_site}{activation_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return redirect('users:email_confirmation_sent')


class UserConfirmationSentView(PasswordResetDoneView):
    """
    Контроллер, который отвечает за вывод информации об отправке на почту подтверждения регистрации
    """
    template_name = "users/registration_sent_done.html"
    extra_context = {
        'title': 'На почту отправлена ссылка подтверждения регистрации'
    }


class UserConfirmEmailView(View):
    """
    Контроллер, который отвечает за вывод информации о подтверждении регистрации пользователем
    """
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('users:email_confirmed')
        else:
            return redirect('users:email_confirmation_failed')


class UserConfirmedView(TemplateView):
    """
    Контроллер, который отвечает за вывод информации об успешнойрегистрации пользователем
    """
    template_name = 'users/registration_confirmed.html'


class UserConfirmationFailView(View):
    """
    Контроллер, который отвечает за вывод информации о невозможности зарегистрировать пользователя """
    template_name = 'users/email_confirmation_failed.html'


class ProfileView(UpdateView):
    """
    Контроллер, который отвечает изменение пользователя
    """
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(ListView):
    """
    Контроллер, который отвечает за просмотр пользователей
    """
    model = User
    # permission_required = 'users.view_user'
    extra_context = {
        'title': 'Users list'
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = super().get_queryset()
        elif user.is_staff:
            queryset = super().get_queryset().filter(is_staff=False)
        else:
            queryset = None
        return queryset
