import datetime
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, UpdateView, CreateView
from .filters import AdvertismentFilter, CommentFilter
from .forms import RegistrationForm, MyActivationCodeForm, ProfileEditForm, AdvertismentForm, CommentForm, \
    AdvertismentListForm
from .models import Advertisment, Profile, Category, Comment, Subscriber


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'profile.html'
    form_class = ProfileEditForm
    success_url = '/'

    def get_object(self):
        return self.request.user


class AdvertismentList(ListView):
    model = Advertisment
    template_name = 'advertisments.html'
    context_object_name = 'advertisments'
    ordering = '-time_create'
    form_class = AdvertismentListForm

    def get_queryset(self):
        queryset = super().get_queryset()
        return AdvertismentFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AdvertismentFilter(self.request.GET, queryset=self.get_queryset())
        is_subscriber = False
        if self.request.user.is_authenticated:
            is_subscriber = Subscriber.objects.filter(user=self.request.user).exists()   # подписан на рассылку
        context['is_subscriber'] = is_subscriber
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


def generate_code():
    random.seed()
    return str(random.randint(10000, 99999))


def register(request):
    if not request.user.is_authenticated:
        if request.POST:
            form = RegistrationForm(request.POST or None)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                my_password1 = form.cleaned_data.get('password1')
                u_f = User.objects.get(username=username, email=email, is_active=False)
                code = generate_code()
                if Profile.objects.filter(code=code):
                    # for p in Profile.objects.filter(code=code):
                    #     p.delete()
                    code = generate_code()
                message = code
                user = authenticate(username=username, password=my_password1)
                now = datetime.datetime.now()
                Profile.objects.create(user=u_f, code=code, date=now)
                send_mail('Код подтверждения', message, 's.gospodchikov@yandex.ru', [email], fail_silently=False)
                if user and user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    form.add_error(None, 'Аккаунт не активирован')
                    return redirect('/activation_code_form/')
            else:
                return render(request, 'register.html', {'form': form})
        else:
            return render(request, 'register.html', {'form': RegistrationForm()})
    else:
        return redirect('user/')


def endreg(request):
    if request.user.is_authenticated:
        return redirect('user/')
    else:
        if request.method == 'POST':
            form = MyActivationCodeForm(request.POST)
            if form.is_valid():
                code_use = form.cleaned_data.get("code")
                if Profile.objects.filter(code=code_use):
                    profile = Profile.objects.get(code=code_use)
                else:
                    form.add_error(None, "Код подтверждения не совпадает.")
                    return render(request, 'activation_code_form.html', {'form': form})
                if not profile.user.is_active:
                    profile.user.is_active = True
                    profile.user.save()
                    login(request, profile.user, backend='django.contrib.auth.backends.ModelBackend')
                    user = request.user
                    registered_group = Group.objects.get(name='registered')
                    if not request.user.groups.filter(name='registered').exists():
                        registered_group.user_set.add(user)             # добавляем пользователя в зарегистрированные
                    profile.delete()
                    return redirect('user/')
                else:
                    form.add_error(None, 'Неизвестный или запрещенный аккаунт')
                    return render(request, 'activation_code_form.html', {'form': form})
            else:
                return render(request, 'activation_code_form.html', {'form': form})
        else:
            form = MyActivationCodeForm()
            return render(request, 'activation_code_form.html', {'form': form})


class AdvertismentCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('fsite.add_advertisment')
    template_name = 'advertisment_create.html'
    form_class = AdvertismentForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        Advertisment.objects.create(
            user=request.user,
            category=Category.objects.get(id=request.POST['category']),
            heading=request.POST['heading'],
            body=request.POST['body']
        )
        return redirect('/')

    def get_object(self, **kwargs):
        _id = self.kwargs.get('pk')
        return Advertisment.objects.get(pk=_id)


class AdvertismentUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('fsite.change_advertisment')
    template_name = 'advertisment_create.html'
    form_class = AdvertismentForm
    success_url = '/'

    def get_object(self, **kwargs):
        _id = self.kwargs.get('pk')
        return_object = Advertisment.objects.get(pk=_id)
        return return_object


class AdvertismentDetail(ListView):
    model = Comment
    template_name = 'advertisment.html'
    context_object_name = 'comments'

    def get_queryset(self):
        queryset = super().get_queryset().filter(advertisment_id=self.kwargs['pk'])     # отклики из нужного объявления
        return CommentFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CommentFilter(self.request.GET, queryset=self.get_queryset())
        advertisment = Advertisment.objects.get(id=self.kwargs['pk'])
        context['advertisment'] = advertisment
        is_author = advertisment.user == self.request.user   # текущий пользователь - автор просматриваемого объявления
        context['is_author'] = is_author
        context['num_comments'] = Comment.objects.filter(advertisment=self.kwargs['pk']).count()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


class CommentCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('fsite.add_comment')
    template_name = 'comment_create.html'
    form_class = CommentForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        _id = self.kwargs.get('pk')
        advertisment = Advertisment.objects.get(pk=_id)
        comment = request.POST['comment']
        Comment.objects.create(
            user=request.user,
            comment=comment,
            advertisment=advertisment
        )
        email = advertisment.user.email
        url = 'http://' + Site.objects.get_current().domain + ':8000/' + str(_id) + '/'
        message = f'Пользователь {request.user} оставил отклик с текстом - {comment}, в объявлении {url}'
        send_mail('Новый отклик на ваше объявление', message, 's.gospodchikov@yandex.ru', [email], fail_silently=False)
        return redirect('/' + str(_id))

    def get_object(self, **kwargs):
        _id = self.kwargs.get('pk')
        return Advertisment.objects.get(pk=_id)


def comment_accept(request, *args, **kwargs):
    _id = kwargs.get('pk')
    comment = Comment.objects.get(id=_id)
    comment.hide(False)
    email = comment.user.email  # email для отправки уведомления пользователю
    url = 'http://' + Site.objects.get_current().domain + ':8000/'
    message = f'Пользователь {request.user} принял ваш комментарий с текстом - {comment.comment}, на сайте {url}'
    send_mail('Ваш отклик опубликован', message, 's.gospodchikov@yandex.ru', [email], fail_silently=False)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def comment_delete(request, *args, **kwargs):
    _id = kwargs.get('pk')
    comment = Comment.objects.get(id=_id)
    comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def subscribe(request):
    user = request.user
    if Subscriber.objects.filter(user=user).exists():
        Subscriber.delete_subscriber(user)
    else:
        Subscriber.add_subscriber(user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
