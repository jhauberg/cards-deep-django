from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login

from core.models import Player, Card
from core.views import start_new_session, get_current_state


def index(request):
    try:
        player = Player.objects.get(pk=request.user.id)
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
            User.objects.create_user(
                username, email, password)
        except Exception:
            return HttpResponse(status=500)
        else:
            login(request)

        return HttpResponseRedirect('/')

    return HttpResponse(status=500)


def player_or_guest(request):
    if 'username' not in request.POST or 'password' not in request.POST:
        try:
            user = User.objects.get(pk=1)
        except User.DoesNotExist:
            user = None
    else:
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = authenticate(
                username=username,
                password=password)
        except:
            user = None

    return user


def login(request):
    if request.method == 'GET':
        return render(
            request,
            'login.html')

    if request.method == 'POST':
        user = player_or_guest(request)

        if user is None:
            return HttpResponse(status=500)

        if user.is_active:
            auth_login(request, user)

            next_path = request.GET.get('next', None)

            if next_path is None:
                next_path = '/'

            return HttpResponseRedirect(next_path)

    return HttpResponse(status=500)


def logout(request):
    auth_logout(request)

    next_path = request.GET.get('next', None)

    if next_path is None:
        next_path = '/'

    return HttpResponseRedirect(next_path)


def begin(request):
    if request.method != 'POST':
        return HttpResponse(status=500)

    session = start_new_session(request)

    if session is None:
        return HttpResponse(status=500)

    return HttpResponseRedirect('/play/%s' % (session.id))


def resume(request, session_id):
    state = get_current_state(request, session_id)

    if state is None:
        return HttpResponse(status=500)

    return render(
        request,
        'board.html', {
            'state': state
        }
    )


def card(request, session_id):
    try:
        card_id = request.GET['id']
        card = Card.objects.get(pk=card_id)
    except Card.DoesNotExist:
        card = None

    if card is None:
        return HttpResponse(status=500)

    return render(
        request,
        'parts/card.html', {
            'card': card
        }
    )


def preferences(request):
    return HttpResponse('your preferences')


def profile(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        player = None

    if player is None:
        return HttpResponse('profile does not exist.')

    return HttpResponse('profile for: %s' % (player))
