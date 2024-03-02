import datetime
from typing import Any
from django.forms import ModelForm
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import FormView
from django.contrib import messages
from bank.forms import PrivateRequestForm, PublicRequestForm
from bank.models import DonationRequest
from django.contrib.auth.decorators import login_required
from django.db.models.query import Q

from users.models import Profile

# Create your views here.


def passView(req):
    return redirect('home')


def createRequestView(req: HttpRequest):
    ctx: dict[str, Any] = {
        'title': 'Create donation request',
        'btnTxt': 'Submit'
    }
    targetUserId = req.GET.get('to', None)
    targetUserProfile = None
    if targetUserId != None:
        all = Profile.objects.filter(user=targetUserId).get()
        if len(all) > 0 and all[0].available == True:
            targetUserProfile = all[0]

    if targetUserId != None and targetUserProfile == None:
        messages.error(req, 'The requested user is not available')
        return redirect('home')

    if req.method == 'GET':
        if targetUserProfile != None:
            ctx['form'] = PrivateRequestForm(
                initial={'targetDonor': targetUserId, 'bloodGroup': targetUserProfile.bloodGroup, 'createdBy': req.user})
            ctx['userName'] = targetUserProfile.user.first_name + \
                ' ' + targetUserProfile.user.last_name
            ctx['bg'] = targetUserProfile.bloodGroup
        else:
            ctx['form'] = PublicRequestForm(initial={'createdBy': req.user})
        return render(req, 'request_form.html', ctx)

    form: ModelForm | None = None

    if targetUserProfile != None:
        form = PrivateRequestForm(req.POST)
    else:
        form = PublicRequestForm(req.POST)
    if form.is_valid():
        # form.cleaned_data['createdBy'] = req.user.id
        DonationRequest.objects.create(
            # createdAt=form.cleaned_data['createdAt'],
            createdBy=req.user,
            bloodGroup=form.cleaned_data.get('bloodGroup', None),
            date=form.cleaned_data.get('date', None),
            contactNumber=form.cleaned_data.get('contactNumber', None),
            targetDonor=form.cleaned_data.get('targetDonor', None),
            acceptedBy=form.cleaned_data.get('acceptedBy', None),
            description=form.cleaned_data.get('description', None),
            cancelled=form.cleaned_data.get('cancelled', False),
        )
        return redirect('dashboard')
    ctx['form'] = form
    return render(req, 'request_form.html', ctx)


@login_required
def dashboardView(req: HttpRequest):
    reqs = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=None, acceptedBy=None).all()[:6]
    preqs = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=req.user, acceptedBy=None, cancelled=False).all()[:6]
    history = DonationRequest.objects.filter(Q(cancelled=True) | Q(
        acceptedBy=req.user)).order_by('updatedAt').all()
    ctx = {
        'reqs': reqs,
        'preqs': preqs,
        'history': history
    }
    return render(req, 'dashboard.html', ctx)


@login_required
def acceptRequestView(req, id):
    requests = DonationRequest.objects.filter(id=id).all()
    if len(requests) == 0:
        messages.error(req, 'The donation request was not found')
        return redirect('dashboard')

    r = requests[0]
    r.acceptedBy = req.user
    r.updatedAt = datetime.datetime.now()
    r.save()
    messages.success(req, 'You accepted the donation request')
    return redirect('dashboard')
