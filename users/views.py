from typing import Any
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from bank.models import DonationRequest

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
        form.save()
        messages.success(self.request, 'Registration successful')
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
    createdOnes = DonationRequest.objects.filter(createdBy=req.user).order_by('-updatedAt').all()

    ctx = {
        'profile': profile,
        'records': createdOnes
    }
    return render(req, 'profile.html', context=ctx)
