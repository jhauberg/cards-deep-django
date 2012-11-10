# Status

CURRENTLY NOT PLAYABLE!

-----

# Cards Deep

A web-based implementation of a [fast-paced card game](https://github.com/shrt/cards-deep-ruleset). Python and Django. 

It's supposed to end up looking something like this:

![Mockup](https://raw.github.com/shrt/cards-deep-django/master/mockup.png)

Card iconography comes straight off the fantastic [Game Icons](http://game-icons.net/) resource. Thank you!

## How to

This particular implementation provides registered players with a persistent gamestate, which means that the current game session can be accessed from anywhere.

But that also means that the game has to be installed with a database and hosted on a server - it is pretty easy to get it running on localhost, though.

### Install

To get the game up and running, you need to have `python` and `django` installed. After that you just go:

    $ cd cards-deep-django

And then:

    $ python manage.py syncdb
    $ python manage.py runserver

Now you can open a browser and hit up [localhost](http://127.0.0.1:8000) to register a user and start playing.

### Modify

All the cards are defined in `initial_data.json` as instances of `core.carddetail`. The amount of these should not be modified, as defined in the [rules](https://github.com/shrt/cards-deep-ruleset). But the existing ones can have their names, description and flavor texts changed. e.g:

```json
{
    "pk": 33,
    "model": "core.carddetail",
    "fields": {
        "kind": 2,
        "name": "Ogre",
        "value": 14
    }
}
```

Could be changed to:

```json
{
    "pk": 33,
    "model": "core.carddetail",
    "fields": {
        "kind": 2,
        "name": "Armada",
        "description": "An armada of enemy spaceships.",
        "flavor": "Fleeing is always an option.",
        "value": 14
    }
}
```

The %-chance values can also be tweaked for gameplay balance. Look in `core\rules.py` for the `draw_single` function. 

Try playing with these values:

```python
card_should_be_beneficial = roll(0, 100) >= 60 # 40 chance of not being a monster card
card_should_be_special = roll(0, 100) >= 95    # 5% chance of being special
```

And these:

```python
weapon_range = range(0, 45)
weapon_part_range = range(45, 75)
potion_range = range(75, 90)
treasure_range = range(90, 100)
```