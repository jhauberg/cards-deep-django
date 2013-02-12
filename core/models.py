from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from fields import PositiveSmallIntegerRangeField

CARD_KIND_WEAPON = 0
CARD_KIND_POTION = 1
CARD_KIND_MONSTER = 2
CARD_KIND_SCRAP = 3
CARD_KIND_TREASURE = 4

CARD_KINDS = (
    (CARD_KIND_WEAPON, 'Weapon'),
    (CARD_KIND_POTION, 'Potion'),
    (CARD_KIND_MONSTER, 'Monster'),
    (CARD_KIND_SCRAP, 'Scrap'),
    (CARD_KIND_TREASURE, 'Treasure'),
)


class Player(models.Model):
    user = models.OneToOneField(User)
    active_session = models.OneToOneField('Session', null=True, blank=True)

    def __unicode__(self):
        if self.user.first_name and self.user.last_name:
            return u'%s %s' % (self.user.first_name, self.user.last_name)
        else:
            return u'%s' % (self.user.first_name)


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    """
    Create a matching profile whenever a user object is created.
    """
    if created:
        profile, new = Player.objects.get_or_create(user=instance)


class Session(models.Model):
    belongs_to_player = models.ForeignKey('Player')

    # Player's health attribute. Assumes only positive values are allowed, since 0 or less is a loss.
    health = models.PositiveSmallIntegerField(default=20)
    # To keep track of how many cards have been moved from the current room, since the last skip was activated.
    # Defaults to negative value so that we can allow skipping on the very first turn.
    amount_of_cards_moved_since_last_skip = models.IntegerField(default=-1)

    room_stack = models.ForeignKey('Stack', related_name='room_stack')
    equipment_stack = models.ForeignKey('Stack', related_name='equipment_stack')
    you_stack = models.ForeignKey('Stack', related_name='you_stack')
    treasure_stack = models.ForeignKey('Stack', related_name='treasure_stack')
    forge_stack = models.ForeignKey('Stack', related_name='forge_stack')
    discard_stack = models.ForeignKey('Stack', related_name='discard_stack')

    score = models.IntegerField(default=0)
    score_multiplier = models.IntegerField(default=1)

    def __unicode__(self):
        return u'%s with Health: %s' % (self.belongs_to_player, self.health)


class CardDetail(models.Model):
    kind = models.PositiveSmallIntegerField(choices=CARD_KINDS)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=180, blank=True)
    flavor = models.CharField(max_length=100, blank=True)
    value = PositiveSmallIntegerRangeField(min_value=2, max_value=14, null=True, blank=True)

    def __unicode__(self):
        if self.value is None:
            return u'(%s)' % (self.name)
        else:
            return u'%s (%s)' % (self.value, self.name)


class Card(models.Model):
    belongs_to_session = models.ForeignKey('Session')
    # Separating the properties into its own table allows us to have several cards of
    # the same kind, but without duplicating data.
    details = models.ForeignKey('CardDetail')
    stack = models.ForeignKey('Stack', null=True)
    order_in_stack = models.IntegerField(default=-1)
    is_special = models.BooleanField(default=False)  # Any card has a chance to be special...

    def can_be_moved(self, to_stack):
        if self.stack:
            # Card is already in a stack
            if not self.stack.is_editable:
                # Stack allows manipulation
                return False

            if self.stack == to_stack:
                return False

        return True

    def __unicode__(self):
        if self.is_special:
            return u'%s*' % (self.details)
        else:
            return u'%s' % (self.details)


def get_first_element(iterable, default=None):
    if iterable:
        for item in iterable:
            return item

    return default


class Stack(models.Model):
    # todo: orderby! a stack is not just a pile of cards, it's a list of cards in a specific order
    # cards probably need to have a field that specified this order, because cards can be put
    # into any stack, and would then not be orderable just by pk alone..
    is_editable = models.BooleanField(default=True)

    def belongs_to_session(self, session):
        if session:
            if (session.room_stack == self or
                session.equipment_stack == self or
                session.you_stack == self or
                session.treasure_stack == self or
                session.discard_stack == self or
                session.forge_stack == self):
                return True

        return False

    def get_bottom(self):
        #return get_first_element(Card.objects.filter(stack=self).reverse()[:1])
        return get_first_element(Card.objects.filter(stack=self).order_by('order_in_stack')[:1])

    def get_top(self):
        return get_first_element(Card.objects.filter(stack=self).order_by('-order_in_stack')[:1])

    def get_all_cards(self):
        return Card.objects.filter(stack=self)

    def count(self):
        return len(self.get_all_cards())

    def is_empty(self):
        return self.count() == 0

    def push(self, card):
        try:
            card.stack = self
            card.order_in_stack = self.count()
            card.save()
        except:
            return False

        return True

    def push_many(self, cards):
        stacked_cards = []

        for card in cards:
            if self.push(card):
                stacked_cards.append(card)

        return stacked_cards

    def pop_specific(self, card):
        cards = self.get_all_cards()

        if card in cards:
            try:
                card.stack = None
                card.order_in_stack = -1
                card.save()
            except:
                return False
        else:
            return False

        return True

    def pop(self):
        try:
            self.pop_specific(self.get_top())
        except:
            return False

        return True

    def __unicode__(self):
        return u'%s' % (self.id)
