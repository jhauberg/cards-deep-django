from models import Player, Session, Card, CardDetail, CARD_KINDS, Stack
from rules import start

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

def current_state(session):
    """
    Returns all information on the current state of the active game session.
    """
    if not session:
        return None

    current_room_cards = list(session.room_stack.get_all_cards())
    current_equipment_cards = list(session.equipment_stack.get_all_cards())
    current_you_cards = list(session.you_stack.get_all_cards())
    current_treasure_cards = list(session.treasure_stack.get_all_cards())
    current_forge_cards = list(session.forge_stack.get_all_cards())

    return {
        'health': int(session.health),
        'stacks': [
            { 'name': 'room', 'id': session.room_stack.id, 'cards': current_room_cards },
            { 'name': 'equipment', 'id': session.equipment_stack.id, 'cards': current_equipment_cards },
            { 'name': 'you', 'id': session.you_stack.id, 'cards': current_you_cards },
            { 'name': 'treasure', 'id': session.treasure_stack.id, 'cards': current_treasure_cards },
            { 'name': 'forge', 'id': session.forge_stack.id, 'cards': current_forge_cards }
        ]
    }

def get_current_state(request, session_id):
    try:
        player = Player.objects.get(pk = request.user.id)
    except Player.DoesNotExist:
        return None

    try:
        session = Session.objects.get(pk = session_id)
    except Session.DoesNotExist:
        return None

    state = None

    if session_is_valid(request, session):
        state = current_state(session)

    return state

def start_new_session(request):
    try:
        player = Player.objects.get(pk = request.user.id)
    except Player.DoesNotExist:
        player = None

    session = None

    if player is not None:
        session = start(player)       

    return session