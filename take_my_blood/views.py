from django.http import HttpRequest
from django.shortcuts import render
from django.db.models.query import Q

from users.models import Profile


def homeView(req: HttpRequest):
    q = Profile.objects.filter(available=True)
    if req.user.is_authenticated:
        q = q.filter(~Q(user=req.user))
    donors = q.order_by(
        'lastDonationDate').all()[:12]
    ctx = {
        'donors': donors
    }
    return render(req, 'home.html', ctx)
