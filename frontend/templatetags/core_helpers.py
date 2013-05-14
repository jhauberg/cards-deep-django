from django import template

register = template.Library()

from core.models import CARD_KIND_WEAPON, CARD_KIND_POTION, CARD_KIND_MONSTER, CARD_KIND_SCRAP, CARD_KIND_TREASURE


@register.filter
def kind_name(kind):
    kind_name = None

    if kind == CARD_KIND_WEAPON:
        kind_name = 'weapon'
    elif kind == CARD_KIND_POTION:
        kind_name = 'potion'
    elif kind == CARD_KIND_MONSTER:
        kind_name = 'monster'
    elif kind == CARD_KIND_SCRAP:
        kind_name = 'scrap'
    elif kind == CARD_KIND_TREASURE:
        kind_name = 'treasure'

    return kind_name
