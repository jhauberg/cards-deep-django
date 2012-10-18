from models import Player, Session

def session_is_valid(request, session):
    if not session:
        return False

    try:
        player = Player.objects.get(pk = request.user.id)
    except Player.DoesNotExist:
        return False

    if session.belongs_to_player != player:
        return False

    return True