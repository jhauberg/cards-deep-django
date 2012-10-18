from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings

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
    return HttpResponse('sign up to play')

def login(request):
    return HttpResponse('logged in')

def logout(request):
    return HttpResponse('logged out')

def begin(request):
    return HttpResponse('game started')

def resume(request, session_id):
    return HttpResponse('game resumed')

def end(request):
    return HttpResponse('game ended')

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