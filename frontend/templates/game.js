var FIDGET_AMOUNT_DISCARD = 12;
var FIDGET_AMOUNT = 6;

var state = {}

var didShowHintLastMove = false;

function refresh(newState) {
    var previousState = state;

    if (newState) {
        state = newState;

        onStateChanged(previousState);
    } else {
        getState(function(response) {
            refresh(response);
        });
    }
}

function onStateChanged(previousState) {
    updateScore(previousState.score);
    updateHealth(previousState.health);
    updateHint();

    determineStrikeAvailability();
    determineForgeAvailability();
    determineBuffAvailability();

    if (state.is_lost) {
        toggleButton($('#strike-action'), false);
        toggleButton($('#forge-action'), false);
        toggleButton($('#treasure-action'), false);

        $('.card').unbind('mouseup mouseenter mouseleave');
        $('.health').css('opacity', 0.4);

        $('#you li').last().append('<div id="killer-label">Your killer!</div>');
    }
}

function determineStrikeAvailability() {
    toggleButton($('#strike-action'), 
        state.stacks[1].cards.length > 0);

    var strike_amount = 
        state.stacks[1].cards.length > 0 && 
        state.stacks[2].cards.length > 0 ? 
            state.stacks[2].cards.length : 0;

    $('#strike-action').html(
        'STRIKE<br>' + 
        (strike_amount > 0 ? strike_amount : '') +
        (strike_amount > 1 ? '<div id="strike-action-multiplier">X ' + strike_amount + '</div>' : '') +
        (state.score_multiplier > 0 ? '<div id="strike-action-bonus-multiplier">+ ' + (state.score_multiplier * 10 + 100) + '%</div>' : ''));
}

function determineForgeAvailability() {
    toggleButton($('#forge-action'), 
        state.stacks[4].cards.length >= 2 &&
        state.stacks[1].cards.length == 0);

    $('#forge-action').html('FORGE<br>' + 
        (state.stacks[4].cards.length > 0 ? '' + state.stacks[4].cards.length : ''));
}

function determineBuffAvailability() {
    toggleButton($('#treasure-action'), 
        state.stacks[3].cards.length > 0);

    $('#treasure-action').html('BUFF<br>' + 
        (state.stacks[3].cards.length > 0 ? '' + state.stacks[3].cards.length : ''));
}

function updateHealth(previousHealth) {
    var healthDelta = state.health - previousHealth;
    var amountInPixels = state.health * 6;

    $('.health-bar').css("width", amountInPixels);
    $('.health-ui .value').first().text(state.health);

    if (!isNaN(healthDelta) && healthDelta != 0) {
        floatDamageNumbers(healthDelta);
    }
}

function updateScore(previousScore) {
    var scoreDelta = state.score - previousScore;

    $('.scoreboard .scoreboard-value').first().text('' + state.score);

    if (!isNaN(scoreDelta) && scoreDelta != 0) {
        floatScoreNumbers(scoreDelta);
    }
}

function updateHint() {
    var hint = $('#hint-skip');

    if (state.can_skip_on_next_move) {
        didShowHintLastMove = true;

        hint.css({
            'top': '-16px',
            'visibility': 'visible',
            'opacity': 0
        });

        hint.animate({
            opacity: 1,
            top: 0
        }, 200);
    } else if (didShowHintLastMove) {
        didShowHintLastMove = false;

        hint.animate({
            opacity: 0,
            top: '-16px'
        }, 200, function() {
            hint.css({
                'visibility': 'hidden'
            });
        });
    }
}

function selectCardInRoom(element, selected) {
    var amount = selected ? '12px' : '0px';

    $(element).stop().animate({
            top: amount
        }, 'fast'
    );
}

function selectMap(selected) {
    var amount = selected ? '8px' : '0px';
    
    $('#map-bottom').stop().animate({
            left: amount
        }, 'fast'
    );
}

function drawIntoRoom(card, delay) {
    $.get('{% url card state.session_id %}?id=' + card.id, function(data) {
        $('#room').append(data);
        
        var card_element = $('#card-' + card.id);

        card_element.css({
            'left': '80px',
            'opacity': 0
        });

        card_element.delay(delay).animate({
            left: '0px',
            opacity: 1
        }, 200, function() {
            bindCardActions(card_element);
        });
    });
}

function drawIntoEquipment(card, delay) {
    $.get('{% url card state.session_id %}?id=' + card.id, function(data) {
        $('#forge').append(data);
        
        var equipment = $('#equipment');
        var card_element = $('#card-' + card.id);
        
        animateMove(card_element, equipment);
    });
}

function drawTopIntoRoom() {
    var room_stack = state.stacks[0];
    var new_card = room_stack.cards[room_stack.cards.length - 1];

    drawIntoRoom(new_card);
}

function drawAllIntoRoom() {
    var room_stack = state.stacks[0];

    for (var i = 0; i < room_stack.cards.length; i++) {
        var card = room_stack.cards[i];

        drawIntoRoom(card, 100 * i);
    }
}

function animateDiscard(card) {
    var discarded = $('#discarded');

    card.animate({
        opacity: 0
    }, 300, function() {
        card.removeAttr('style');
        card.removeClass('monster treasure scrap potion weapon');
        card.empty();

        discarded.append(this);

        fidget(card, FIDGET_AMOUNT_DISCARD);

        card.animate({
            opacity: 1
        }, 100);
    });
}

function animateMove(card, stack, completed) {
    var stackOffset = stack.offset();
    var cardOffset = card.offset();

    var dx = stackOffset.left - cardOffset.left;
    var dy = stackOffset.top - cardOffset.top;

    card.unbind('mouseup mouseenter mouseleave');

    card.animate({
        top: dy <= 0 ? 40 : -40
    }, 200, function() {
        card.animate({
            top: dy,
            left: dx
        }, 500, function() {
            card.removeAttr('style');

            stack.append(this);

            fidget(card, FIDGET_AMOUNT);

            if (completed) {
                completed();
            }
        });
    });
}

function floatNumbers(numbersElement, inSelector) {
    $(inSelector).append(numbersElement);

    $(numbersElement).animate({
        top: -100,
        opacity: 0
    }, 4000, function() {
        $(this).remove();
    });
}

function floatDamageNumbers(damage) {
    var $floater = $(
        '<div class="value negative">' + 
        (damage > 0 ? '+' : '') + damage + 
        '</div>');

    floatNumbers($floater, '.health-ui', damage);
}

function floatScoreNumbers(score) {
    var $floater = $(
        '<div class="scoreboard-value negative">' + 
        (score > 0 ? '+' : '') + score + 
        '</div>');

    floatNumbers($floater, '.scoreboard', score);
}

function bindCardActions(selector) {
    $(selector).mouseenter(
        function() {
            selectCardInRoom($(this), true);
        }
    );

    $(selector).mouseleave(
        function() {
            selectCardInRoom($(this), false);
        }
    );

    $(selector).mouseup(
        function() {
            var card = $(this);
            var cardId = this.id.replace('card-', '');

            var moveToStackId = -1;
            var moveToStack = null;

            if (card.hasClass('weapon')) {
                moveToStackId = state.stacks[1].id;
                moveToStack = $('#equipment');
            } else if (card.hasClass('monster') || card.hasClass('potion')) {
                moveToStackId = state.stacks[2].id;
                moveToStack = $('#you');
            } else if (card.hasClass('treasure')) {
                moveToStackId = state.stacks[3].id;
                moveToStack = $('#treasure');
            } else if (card.hasClass('scrap')) {
                moveToStackId = state.stacks[4].id;
                moveToStack = $('#forge');
            }

            if ((card != null && cardId != -1) && 
                (moveToStack != null && moveToStackId != -1)) {
                move(cardId, moveToStackId, function(response) {
                    if (response.success) {
                        var shouldBeDiscardedImmediately = 
                            (card.hasClass('monster') && state.stacks[1].cards.length == 0) ||
                            (card.hasClass('potion'));

                        animateMove(card, moveToStack, function() {
                            refresh(response.state);

                            if (!state.is_lost) {
                                drawTopIntoRoom();
                            }

                            if (shouldBeDiscardedImmediately) {
                                var discarded = $('#discarded');

                                animateMove(card, discarded, function() {
                                    animateDiscard(card);
                                });
                            }
                        });
                    }
                });
            }
        }
    );
}

$("#map").mouseenter(
    function() {
        if (state.can_skip) {
            selectMap(true);
        }
    }
);

$("#map").mouseleave(
    function() {
        if (state.can_skip) {
            selectMap(false);
        }
    }
);

$("#map").click(
    function() {
        if (state.can_skip) {
            skip(function(response) {
                if (response.success) {
                    refresh(response.state);

                    $('#room .card').reverse().each($).wait(100, function(index) {
                        var card = $(this);
                        var discarded = $('#discarded');

                        animateMove(card, discarded, function() {
                            animateDiscard(card);
                        });
                    }).all().wait(800, function() {
                        drawAllIntoRoom();
                    });
                }
            });

            selectMap(false);
        }
    }
);

// fidget with the cards so the stacks looks messy initially
$('#discarded .card').each(function(index) {
    fidget($(this), FIDGET_AMOUNT_DISCARD);
});

$('#equipment .card').each(function(index) {
    fidget($(this), FIDGET_AMOUNT);
});

$('#you .card').each(function(index) {
    fidget($(this), FIDGET_AMOUNT);
});

$('#treasure .card').each(function(index) {
    fidget($(this), FIDGET_AMOUNT);
});

$('#forge .card').each(function(index) {
    fidget($(this), FIDGET_AMOUNT);
});

$('.button').each(function(index) {
    $(this).mousedown(function() {
        if (!$(this).hasClass('disabled')) {
            $(this).addClass('button-pressed');
        }
    });

    $(this).mouseleave(function() {
        $(this).removeClass('button-pressed');
    });

    $(this).mouseup(function() {
        $(this).removeClass('button-pressed');
    });
});

$('#strike-action').mouseup(function() {
    if ($(this).hasClass('disabled')) {
        return;
    }

    var discarded = $('#discarded');

    clear(state.stacks[1].id, function(response) {
        if (response.success) {
            if (state.stacks[1].cards.length > 0) {
                $('#equipment .card').reverse().each($).wait(50, function(index) {
                    var card = $(this);
            
                    animateMove(card, discarded, function() {
                        refresh(response.state);

                        animateDiscard(card);
                    });
                });
            }

            if (state.stacks[2].cards.length > 0) {
                $('#you .card').reverse().each($).wait(50, function(index) {
                    var card = $(this);
        
                    animateMove(card, discarded, function() {
                        animateDiscard(card);
                    });
                });
            }
        }
    });
});

$('#forge-action').mouseup(function() {
    if ($(this).hasClass('disabled')) {
        return;
    }

    var discarded = $('#discarded');

    if (state.stacks[4].cards.length > 0) {
        clear(state.stacks[4].id, function(response) {
            if (response.success) {
                refresh(response.state);

                var new_card = state.stacks[1].cards[0];

                $('#forge .card').reverse().each($).wait(50, function(index) {
                    var card = $(this);
                    var discarded = $('#discarded');

                    animateMove(card, discarded, function() {
                        animateDiscard(card);
                    });
                }).all().wait(500, function() {
                    drawIntoEquipment(new_card, 100);
                });
            }
        });
    }
});

$('#treasure-action').mouseup(function() {
    if ($(this).hasClass('disabled')) {
        return;
    }

    var discarded = $('#discarded');

    if (state.stacks[3].cards.length > 0) {
        clear(state.stacks[3].id, function(response) {
            if (response.success) {
                refresh(response.state);

                $('#treasure .card').reverse().each($).wait(50, function(index) {
                    var card = $(this);
                    var strike_button = $('#strike-action');
                    var discarded = $('#discarded');

                    animateMove(card, strike_button, function() {
                        animateMove(card, discarded, function() {
                            animateDiscard(card);
                        });
                    });
                });
            }
        });
    }
});

$('#menu-help').mouseup(function() {
    var manual = $('.manual');
    var stats = $('.stats');

    stats.css('visibility', 'hidden');

    toggleVisibility(manual);
});

$('#menu-stats').mouseup(function() {
    var manual = $('.manual');
    var stats = $('.stats');

    manual.css('visibility', 'hidden');

    toggleVisibility(stats);
});

$('#menu-next').mouseup(function() {
    $.post("{% url begin %}", 
        { 
            'csrfmiddlewaretoken': '{{ csrf_token }}',
        },
        function(response) {
            window.location.href = window.location.href.replace(
                '/play/{{ state.session_id }}', 
                '/play/{{ state.session_id|add:"1" }}');
        }
    );
});

bindCardActions('#room .card');

refresh();