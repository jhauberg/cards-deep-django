import logging

logger = logging.getLogger(__name__)

from models import Session, Card, CardDetail, Stack
from models import CARD_KIND_WEAPON, CARD_KIND_POTION, CARD_KIND_MONSTER, CARD_KIND_SCRAP, CARD_KIND_TREASURE

import random

ROOM_CAPACITY = 5
REQUIRED_TURNS_BEFORE_SKIPPING = 5


def roll(min, max):
    return random.randint(min, max)


def get_random_card_id_in_value_range(min, max, offset):
    card_id = roll(
        min + offset,
        max + offset)

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
        belongs_to_player=player,

        room_stack=room_stack,
        you_stack=you_stack,
        equipment_stack=equipment_stack,
        forge_stack=forge_stack,
        treasure_stack=treasure_stack,
        discard_stack=discard_stack
    )

    session.save()

    # Draw the first 5 cards.
    initial_room_cards = draw(session, ROOM_CAPACITY)

    # Put the initial cards in place.
    room_stack.push_many(initial_room_cards)

    # If everything went as expected, activate the session by hooking it up to the player.
    player.active_session = session
    player.save()

    return session


def draw_single(session, properties=None):
    """
    Attempts drawing a single card.
    Can optionally be given specific properties, determined randomly otherwise.
    """
    if session is None:
        return None

    card_should_be_special = False

    if properties is None:
        card_should_be_beneficial = roll(0, 100) >= 60  # 40 chance of not being a monster card
        card_should_be_special = roll(0, 100) >= 95     # 5% chance of being special

        details_id = None

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

        if details_id is None:
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
    if session is None:
        return None

    if amount <= 0:
        return None

    cards = []

    for i in range(0, amount):
        card = draw_single(session)

        if card is not None:
            cards.append(card)

    return cards


def can_activate_stack(session, stack):
    """
    Determines whether a stack can be activated in its current state.
    """
    if not session or not stack:
        return False

    # Assuming an empty stack can never be activated.
    if stack.is_empty():
        return False

    if stack == session.room_stack:
        # The current room can never be activated.
        return False

    if stack == session.discard_stack:
        # The discarded stack can never be activated.
        return False

    if stack == session.equipment_stack or stack == session.you_stack:
        # No special rules for weapons/monsters.
        pass

    if stack == session.forge_stack:
        all_forgeable_cards = stack.get_all_cards()

        if all_forgeable_cards:
            amount_of_forgeable_cards = len(all_forgeable_cards)

            if amount_of_forgeable_cards < 2:
                # The forge stack can only be activated when at least 2 scrap cards are placed here.
                return False

            # todo: should forged cards always be special? (this means you can always override the current stack! potential game changer)
            if not session.equipment_stack.is_empty():
                return False

    return True


def activate_stack(session, stack):
    """
    Attempts activating/clearing a stack.
    """
    if not session or not stack:
        return False

    if not can_activate_stack(session, stack):
        return False

    if stack == session.equipment_stack or stack == session.you_stack:
        discard_many(session, session.equipment_stack.get_all_cards())

        monster_cards = session.you_stack.get_all_cards()
        monster_cards_discarded = discard_many(session, monster_cards)

        score = monster_cards_discarded * monster_cards_discarded * session.score_multiplier

        session.score += score
        session.score_multiplier = 1
        session.save()

    if stack == session.treasure_stack:
        # apply multiplier to strike (i.e. score = (monsters * monsters) * treasures)
        treasure_cards = session.treasure_stack.get_all_cards()
        treasure_cards_discarded = discard_many(session, treasure_cards)

        score_multiplier = treasure_cards_discarded

        session.score_multiplier += score_multiplier
        session.save()

        pass

    if stack == session.forge_stack:
        # Draw a new weapon card that is valued depending on how many cards were spent.

        # Attempt discarding all cards that were spent creating a weapon.
        value = discard_many(session, session.forge_stack.get_all_cards())

        if value <= 0:
            return False

        details_id = get_random_weapon_id_in_value_range(value, value)

        if details_id is None:
            return False

        try:
            properties = CardDetail.objects.get(pk=details_id)
        except CardDetail.DoesNotExist:
            return False

        # Draw the actual card, given the specific properties determined previously.
        weapon_card = draw_single(session, properties)

        # Attempt placing the new weapon on the equipment stack. Keep in mind that it is assumed
        # that the equipment stack is empty when reaching this point.
        did_equip_weapon_card = session.equipment_stack.push(weapon_card)

        if not did_equip_weapon_card:
            logger.error('boooooo!')
            return False

    return True


def can_activate_card(session, card):
    """
    Determines whether a card has properties that allow it to be activated.
    """
    if not session or not card:
        return False

    if card.details.kind is CARD_KIND_POTION:
        if card.stack != session.you_stack:
            # Can only be activated when placed on the You stack.
            return False

    if card.details.kind is CARD_KIND_MONSTER:
        if card.stack != session.you_stack:
            # Can only be activated when placed on the You stack.
            return False

    return True


def activate_card(session, card):
    """
    Attempts activating a card.
    This usually occurs when a card has been successfully moved from the current room.
    """
    if not session or not card:
        return False

    if not can_activate_card(session, card):
        return False

    if card.details.kind is CARD_KIND_POTION:
        restored_health = card.details.value
        current_health = session.health

        current_health += restored_health

        if current_health > 20:
            current_health = 20

        try:
            session.health = current_health
            session.save()
        except:
            return False

        discard(session, card)

    if card.details.kind is CARD_KIND_MONSTER:
        most_recently_played_weapon_card = session.equipment_stack.get_top()

        if most_recently_played_weapon_card and most_recently_played_weapon_card.is_special:
            try:
                # Disable special status as soon as a monster has been placed.
                most_recently_played_weapon_card.is_special = False
                most_recently_played_weapon_card.save()
            except:
                return False

        damage = card.details.value

        if damage:
            if most_recently_played_weapon_card:
                damage -= most_recently_played_weapon_card.details.value

            if damage > 0:
                try:
                    # todo: need to figure out what happens in terms of rollover..
                    # since `health` is unsigned small int does it roll over to maxval when going below 0, like in c?
                    session.health -= damage
                    session.save()
                except:
                    return False

        if not most_recently_played_weapon_card:
            # Monsters only stack if player has a weapon equipped
            session.score += 1
            session.save()

            discard(session, card)

    return True


def can_move(session, card, to_stack):
    """
    Determines whether a card can be moved to a given stack.
    """
    if (not session or
        not card or
        not to_stack):
        return False

    if to_stack == session.room_stack:
        # you can't move cards to the room...
        logger.error(' * card can not be moved to the room!')
        return False

    if to_stack == session.treasure_stack:
        if card.details.kind is not CARD_KIND_TREASURE:
            # Not a treasure card, bail out...
            logger.error(' * only treasure cards can be moved here!')
            return False

        if len(session.treasure_stack.get_all_cards()) >= 10:
            # Treasure stack already holds maximum amount of treasure
            logger.error(' * max treasure reached!')
            return False

    if to_stack == session.forge_stack:
        if card.details.kind is not CARD_KIND_SCRAP:
            # Not a scrap card, bail out...
            logger.error(' * only scrap cards can be moved here!')
            return False

        if len(session.forge_stack.get_all_cards()) >= 10:
            # Forge stack already holds maximum amount of scraps
            logger.error(' * max scraps reached!')
            return False

    if to_stack == session.equipment_stack:
        if card.details.kind is not CARD_KIND_WEAPON:
            # Not a weapon card, bail out...
            logger.error(' * only weapon cards can be moved here!')
            return False

        most_recently_played_weapon_card = session.equipment_stack.get_top()

        if most_recently_played_weapon_card is not None:
            if not card.is_special:
                # Only special cards can be placed on top of the previous weapon as a score multiplier.
                logger.error(' * only special cards can do this!')
                return False

    if to_stack == session.you_stack:
        if card.details.kind is not CARD_KIND_MONSTER and card.details.kind is not CARD_KIND_POTION:
            # Only monsters or potions can be placed here
            logger.error(' * only monster or potion cards can be moved here!')
            return False

        if card.details.kind is CARD_KIND_MONSTER:
            # Card is a monster
            most_recently_played_monster_card = session.you_stack.get_top()

            if most_recently_played_monster_card is not None:
                if card.details.value >= most_recently_played_monster_card.details.value:
                    most_recently_played_weapon_card = session.equipment_stack.get_top()

                    if most_recently_played_weapon_card and not most_recently_played_weapon_card.is_special:
                        # Basically, you can only place monsters of higher value on other monsters if
                        # the current weapon is special.
                        logger.error(' * requires special weapon equipped to do this!')
                        return False

    return True


def move(session, card, to_stack):
    """
    Attempts moving a card into a given stack.
    """
    if not session:
        return False

    if not card or not to_stack:
        return False

    if not card.can_be_moved(to_stack):
        logger.error(' * card can not be moved!')
        return False

    if not can_move(session, card, to_stack):
        logger.error(' * could not allow moving card!')
        return False

    from_stack = card.stack

    if not to_stack.push(card):
        logger.error(' * could not push card on stack!')
        return False

    if to_stack != session.discard_stack:
        if not activate_card(session, card):
            logger.error(' * could not activate card!')
            return False

    if from_stack == session.room_stack:
        if session.amount_of_cards_moved_since_last_skip != -1:
            # If set to -1 that means player has not skipped yet, so we don't need to track this.
            try:
                session.amount_of_cards_moved_since_last_skip += 1
                session.save()
            except:
                logger.error(' * could not increment "cards_moved_since_last_skip"!')
                return False

        try:
            new_card = draw_single(session)

            session.room_stack.push(new_card)
        except:
            logger.error(' * could not draw and push new card to room!')
            return False

    return True


def discard(session, card):
    """
    Discards a card from a game session. The 10 most recently discarded cards are stored.
    """
    if session is None:
        return False

    logger.info('  trying to move %s to "discard_stack"' % (card))

    if move(session, card, session.discard_stack):
        logger.info('    success!')
        all_discarded_cards = session.discard_stack.get_all_cards()

        if all_discarded_cards.count() >= 10:
            oldest_discarded_card = all_discarded_cards.reverse()[:1][0]

            oldest_discarded_card.stack = None
            oldest_discarded_card.save()

        return True

    return False


def discard_many(session, cards):
    """
    Attempts discarding several cards at once.
    """
    if session is None or cards is None:
        return False

    amount_discarded = 0

    for card in cards:
        logger.info('discarding %s' % (card))
        if discard(session, card):
            logger.info('  success!')
            amount_discarded += 1
        else:
            logger.info('  fail!')

    return amount_discarded


def can_skip_on_next_move(session):
    """
    Determines whether a game can have its current room skipped on the following turn.
    """
    if session is None:
        return False

    if (session.amount_of_cards_moved_since_last_skip == REQUIRED_TURNS_BEFORE_SKIPPING - 1):
        return True

    return False


def can_skip(session):
    """
    Determines whether a game can have its current room skipped or not.
    """
    if session is None:
        return False

    if (session.amount_of_cards_moved_since_last_skip == -1 or
        session.amount_of_cards_moved_since_last_skip >= REQUIRED_TURNS_BEFORE_SKIPPING):
        return True

    return False


def skip(session):
    """
    Attempts skipping the current room.
    """
    if session is None:
        return False

    if can_skip(session):
        room_cards = session.room_stack.get_all_cards()

        logger.info('skipping %d cards...' % (len(room_cards)))

        # Note that a new card is drawn into the room automatically for each successful discard
        amount_discarded = discard_many(session, room_cards)

        logger.info('discarded %d cards!' % (amount_discarded))

        try:
            session.amount_of_cards_moved_since_last_skip = 0
            session.save()
        except:
            return False

        return True

    return False
