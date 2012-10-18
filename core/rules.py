CARD_KINDS = (
    (0, 'Weapon'),
    (1, 'Potion'),
    (2, 'Monster'),
    (3, 'Scrap'),
    (4, 'Treasure'),
)

import random

def roll(min, max):
    return random.randint(min, max)