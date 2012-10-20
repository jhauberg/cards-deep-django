from models import Player, Session, Card, CardDetail, CARD_KINDS, Stack

import random

def roll(min, max):
    return random.randint(min, max)

def get_random_card_id_in_value_range(min, max, offset):
    card_id = roll(
        min + offset, 
        max + offset + 1) # + 1 to adjust for exclusive max in random function.

    return card_id

def get_random_weapon_id_in_value_range(min, max):
    if min < 2 or max > 10:
        return None

    return get_random_card_id_in_value_range(min, max, 1)

def get_random_potion_id_in_value_range(min, max):
    if min < 2 or max > 10:
        return None

    return get_random_card_id_in_value_range(min, max, 10)

def get_random_monster_id_in_value_range(min, max):
    if min < 2 or max > 14:
        return None

    return get_random_card_id_in_value_range(min, max, 19)

def start(player):
    """
    Attempts creating a new game session for the given player.
    """
    if player is None:
        return None
        
    # Initialize all the stacks.
    room_stack = Stack()
    room_stack.save()

    you_stack = Stack()
    you_stack.save()

    equipment_stack = Stack()
    equipment_stack.save()

    forge_stack = Stack()
    forge_stack.save()

    treasure_stack = Stack()
    treasure_stack.save()

    discard_stack = Stack()
    discard_stack.save()

    # Begin a new session.
    session = Session(
        # Important to note that a session has to be tied to a player. Same goes for 
        # cards and stacks; they must, ultimately, be tied to a session. Otherwise 
        # it would be possible to move cards between sessions.
        belongs_to_player = player,

        room_stack = room_stack, 
        you_stack = you_stack, 
        equipment_stack = equipment_stack, 
        forge_stack = forge_stack,
        treasure_stack = treasure_stack,
        discard_stack = discard_stack
    )

    session.save()

    # Draw the first 5 cards.
    initial_room_cards = draw(session, 5)

    # Put the initial cards in place.
    room_stack.push_many(initial_room_cards)

    # If everything went as expected, activate the session by hooking it up to the player.
    player.active_session = session
    player.save()

    return session

def draw_single(session, properties=None):
    """
    Attempts drawing a single card.
    Can optionally be given specific properties; otherwise determined randomly.
    """
    if not session:
        return None

    if properties is None:
        card_should_be_beneficial = roll(0, 100) >= 60 # 40 chance of not being a monster card
        card_should_be_special = roll(0, 100) >= 95    # 5% chance of being special

        if card_should_be_beneficial:
            luck = roll(0, 100)

            weapon_range = range(0, 45)
            weapon_part_range = range(45, 75)
            potion_range = range(75, 90)
            treasure_range = range(90, 100)

            if luck in weapon_part_range:
                # Weapon Part
                details_id = 1
            elif luck in treasure_range:
                # Treasure
                details_id = 2
            elif luck in weapon_range:
                # Weapon (2-10)
                details_id = get_random_weapon_id_in_value_range(2, 10)
            elif luck in potion_range:
                # Potion (2-10)
                details_id = get_random_potion_id_in_value_range(2, 10)
        else:
            # Monster (2-14)
            details_id = get_random_monster_id_in_value_range(2, 14)

        if not details_id:
            return None

        try:
            properties = CardDetail.objects.get(pk=details_id)
        except CardDetail.DoesNotExist:
            return None

    try:
        card = Card(
            belongs_to_session=session, 
            details=properties,
            is_special=card_should_be_special
        )

        card.save()
    except:
        return None

    return card

def draw(session, amount):
    """
    Attempts drawing a specific amount of cards.
    """
    if not session:
        return None

    if amount <= 0:
        return None

    cards = []

    for i in range(0, amount):
        card = draw_single(session)

        if card:
            cards.append(card)

    return cards