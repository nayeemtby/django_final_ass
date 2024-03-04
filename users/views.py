from typing import Any
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from bank.models import DonationRequest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from core.mailer import sendMail
from take_my_blood.settings import hostUrl

from users.forms import ProfileUpdateForm, SignupForm
from users.models import Profile

# Create your views here.


class RegistrationView(FormView):
    template_name = 'form.html'
    form_class = SignupForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Register'
        context["btnTxt"] = 'Submit'
        return context

    def form_valid(self, form):
        user = form.save()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f'{hostUrl}/user/activate/{uid}/{token}'
        ctx = {
            'title:': 'Confirm your email to complete registration.',
            'body': f'Follow this link to verify your email: {link}'
        }
        sendMail(user.email, 'Confirm your email', 'email.html', ctx)
        messages.success(
            self.request, 'Please check your email to verify and complete registration')
        return super().form_valid(form)


def updateProfileView(req: HttpRequest):
    ctx = {
        'title': 'Update profile',
        'btnTxt': 'Submit'
    }

    profile = Profile.objects.filter(user=req.user).get()

    if req.method == 'GET':
        ctx['form'] = ProfileUpdateForm(
            instance=profile)
        return render(req, 'form.html', ctx)

    if req.method == 'POST':
        form = ProfileUpdateForm(req.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(req, 'Profile updated')
        else:
            ctx['form'] = form
            return render(req, 'form.html', ctx)
    return redirect('profile')


class UserLoginView(LoginView):
    template_name = 'form.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Login'
        context["btnTxt"] = 'Login'
        return context


@login_required
def logoutView(req: HttpRequest):
    logout(req)
    messages.success(req, 'Successfully logged out')
    return redirect('home')


@login_required
def profileView(req):
    profile = Profile.objects.filter(user=req.user.id).get()
    createdOnes = DonationRequest.objects.filter(
        createdBy=req.user).order_by('-updatedAt').all()

    ctx = {
        'profile': profile,
        'records': createdOnes
    }
    return render(req, 'profile.html', context=ctx)


def activateUser(req: HttpRequest, uid: str, token: str):
    try:
        pk = urlsafe_base64_decode(uid).decode()
        user = User._default_manager.get(pk=pk)
    except (User.DoesNotExist):
        user = None

    if user != None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            req, 'Your email was verified successfully. You can now login')
        return redirect('login')
    messages.error('The link you followed was invalid')
    return redirect('register')
