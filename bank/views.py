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

bloodGroups = [
    'O+',
    'O-',
    'A+',
    'A-',
    'B+',
    'B-',
    'AB+',
    'AB-',
]


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
        all = Profile.objects.filter(user=targetUserId).all()
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
        if targetUserProfile != None:
            form.cleaned_data['bloodGroup'] = targetUserProfile.bloodGroup
            form.cleaned_data['targetDonor'] = targetUserProfile.user
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
    profile = Profile.objects.filter(user=req.user).get()
    reqs = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=None, acceptedBy=None).all()[:6]
    preqs = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=req.user, acceptedBy=None, cancelled=False).all()[:6]
    history = DonationRequest.objects.filter(Q(cancelled=True) | Q(
        acceptedBy=req.user)).order_by('-updatedAt').all()
    ctx = {
        'reqs': reqs,
        'preqs': preqs,
        'history': history,
        'profile': profile,
    }
    return render(req, 'dashboard.html', ctx)


@login_required
def acceptRequestView(req, id):
    profile = Profile.objects.filter(user=req.user).get()
    if profile.bloodGroup == None:
        messages.error(
            req, 'You must set your blood group to be able to accept')
        return redirect('profile')
    if profile.age < 13:
        messages.error(
            req, 'You must be at least 13 years old to be able to accept')
        return redirect('profile')

    requests = DonationRequest.objects.filter(id=id).all()
    if len(requests) == 0:
        messages.error(req, 'The donation request was not found')
        return redirect('dashboard')

    r = requests[0]

    if r.bloodGroup != profile.bloodGroup:
        messages.error(req, 'Your blood group is not the same as requested')
        return redirect('dashboard')

    r.acceptedBy = req.user
    r.updatedAt = datetime.datetime.now()
    r.save()
    profile.lastDonationDate = datetime.date.today()
    profile.save()
    messages.success(req, 'You accepted the donation request')
    return redirect('dashboard')


@login_required
def declineRequestView(req, id):
    profile = Profile.objects.filter(user=req.user).get()
    if profile.bloodGroup == None:
        messages.error(
            req, 'You must set your blood group to be able to accept')
        return redirect('profile')
    if profile.age < 13:
        messages.error(
            req, 'You must be at least 13 years old to be able to accept')
        return redirect('profile')

    requests = DonationRequest.objects.filter(id=id).all()
    if len(requests) == 0:
        messages.error(req, 'The donation request was not found')
        return redirect('dashboard')

    r = requests[0]

    if r.targetDonor != profile.user:
        messages.error(req, 'The request is not for you to decline')
        return redirect('dashboard')

    r.cancelled = True
    r.updatedAt = datetime.datetime.now()
    r.save()
    messages.success(req, 'The request was declined')
    return redirect('dashboard')


@login_required
def allRequestsView(req: HttpRequest):
    selected = req.GET.get('group', None)
    profile = Profile.objects.filter(user=req.user).get()
    q = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=None, acceptedBy=None)
    if selected != None:
        q = q.filter(bloodGroup=selected)
    reqs = q.all()
    ctx = {
        'reqs': reqs,
        'profile': profile,
        'isPublic': True,
        'groups': bloodGroups,
        'selectedGroup': selected,
        'pageTitle': 'Donation requests'
    }
    return render(req, 'all_reqs.html', ctx)


@login_required
def allPrivateRequestsView(req: HttpRequest):
    profile = Profile.objects.filter(user=req.user).get()
    reqs = DonationRequest.objects.filter(
        ~Q(createdBy=req.user), targetDonor=req.user, acceptedBy=None, cancelled=False).all()[:6]
    ctx = {
        'reqs': reqs,
        'profile': profile,
        'pageTitle': 'Exclusive donation requests'
    }
    return render(req, 'all_reqs.html', ctx)


def allDonorsView(req: HttpRequest):
    selected = req.GET.get('group', None)
    q = Profile.objects.filter(available=True)

    if req.user.is_authenticated:
        q = q.filter(~Q(user=req.user))

    if selected != None:
        q = q.filter(bloodGroup=selected)

    donors = q.order_by(
        'lastDonationDate').all()[:12]

    ctx = {
        'donors': donors,
        'groups': bloodGroups,
        'selectedGroup': selected,
    }
    return render(req, 'all_donors.html', ctx)
