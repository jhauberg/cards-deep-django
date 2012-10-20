from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login

from core.models import Player, Session

def index(request):
    try:
        player = Player.objects.get(pk = request.user.id)
    except Player.DoesNotExist:
        player = None

    return render(
        request,
        'index.html', {
            'player': player
        }
    )

def register(request):
    if request.method == 'GET':
        return render(
            request, 
            'register.html')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        try:
            user = User.objects.create_user(
                username, email, password)
        except Exception, e:
            return HttpResponse(status = 500)
        else:
            login(request)

        return HttpResponseRedirect('/')

    return HttpResponse(status = 500)

def login(request):
    if request.method == 'GET':
        return render(
            request, 
            'login.html')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            username = username, 
            password = password)

        if user is None:
            return HttpResponse(status = 500)

        if user.is_active:
            auth_login(request, user)
            
            next_path = request.GET.get('next', None)

            if next_path is None:
                next_path = '/'

            return HttpResponseRedirect(next_path)
    
    return HttpResponse(status = 500)

def logout(request):
    auth_logout(request)

    next_path = request.GET.get('next', None)

    if next_path is None:
        next_path = '/'

    return HttpResponseRedirect(next_path)

def begin(request):
    return HttpResponse('game started')

def resume(request, session_id):
    return HttpResponse('game resumed')

def preferences(request):
    return HttpResponse('your preferences')

def profile(request, player_id):
    try:
        player = Player.objects.get(pk = player_id)
    except Player.DoesNotExist:
        player = None

    if player is None:
        return HttpResponse('profile does not exist.')

    return HttpResponse('profile for: %s' % (player))