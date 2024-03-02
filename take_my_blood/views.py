from django.shortcuts import render


def homeView(req):
    return render(req,'base.html')