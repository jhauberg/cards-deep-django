//////////////
// game rules

function move(card, stack) {
    $.post("{% url perform_action state.session_id 'move' %}", 
        { 
            'csrfmiddlewaretoken': '{{ csrf_token }}',
            'card_id': card,
            'to_stack_id': stack
        },
        function(response) {
            refresh(response.state);
        },
        'json'
    );
}

function skip() {
    $.post("{% url perform_action state.session_id 'skip' %}", 
        { 
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        function(response) {
            refresh(response.state);
        },
        'json'
    );
}

////////
// util

function getRandomBoolean() {
    return Math.random() > 0.5;
}

function getRandomIntInRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function rotate(object, degrees) {
    object.css({
  '-webkit-transform' : 'rotate('+degrees+'deg)',
     '-moz-transform' : 'rotate('+degrees+'deg)',  
      '-ms-transform' : 'rotate('+degrees+'deg)',  
       '-o-transform' : 'rotate('+degrees+'deg)',  
          'transform' : 'rotate('+degrees+'deg)',  
               'zoom' : 1

    });
}

function translate(object, offset) {
    object.css({
        'margin-left': offset.x,
        'margin-top': offset.y
    });
}

function fidget(element, range) {
    var variation = getRandomIntInRange(-range, range);
    var rotation = getRandomBoolean() ? variation : -variation;

    var offset = { 
        x: variation / 2, 
        y: variation 
    };

    rotate(element, rotation);
    translate(element, offset);
}

////////////////////
// game interaction

var state = {}

function onStateChanged(previous_state) {
    updateHealth();
}

function updateHealth() {
    var new_health_amount = state.health;
    var amount_in_pixels = new_health_amount * 6;

    $('.health-bar').css("width", amount_in_pixels);
    $('.health-ui .value').text(new_health_amount);
}

function refresh(newState) {
    var previous_state = state;

    if (newState) {
        state = newState;

        onStateChanged(previous_state);
    } else {
        $.get("{% url state state.session_id %}", 
            { },
            function(response) {
                state = response;

                onStateChanged(previous_state);
            },
            'json'
        );
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

/////////
// hooks

var FIDGET_DISCARD = 12;
var FIDGET_EQUIPMENT = 6;
var FIDGET_YOU = 6;

$("#room .card").mouseenter(
    function() {
        selectCardInRoom(this, true);
    }
);

$("#room .card").mouseleave(
    function() {
        selectCardInRoom(this, false);
    }
);

function animateDiscard(card) {
    var discarded = $('#discarded');

    card.animate({
        opacity: 0
    }, 300, function() {
        card.removeAttr('style');
        card.removeClass('monster treasure scrap potion weapon');
        card.empty();

        discarded.append(this);

        fidget(card, FIDGET_DISCARD);

        card.animate({
            opacity: 1
        }, 100);
    });
}

function animateMove(card, stack, completed) {
    var stack_offset = stack.offset();
    var card_offset = card.offset();

    var dx = stack_offset.left - card_offset.left;
    var dy = stack_offset.top - card_offset.top;

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

            fidget(card, FIDGET_YOU);

            completed();
        });
    });
}

$("#room .card").mouseup(
    function() {
        var card = $(this);
        var card_id = this.id.replace('card-', '');

        var move_to_stack_id = -1;
        var move_to_stack = null;

        if (card.hasClass('weapon')) {
            move_to_stack_id = state.stacks[1].id;
            move_to_stack = $('#equipment');
        } else if (card.hasClass('monster')) {
            move_to_stack_id = state.stacks[2].id;
            move_to_stack = $('#you');
        } else if (card.hasClass('potion')) {
            move_to_stack_id = state.stacks[2].id;
            move_to_stack = $('#you');
        } else if (card.hasClass('treasure')) {
            move_to_stack_id = state.stacks[3].id;
        } else if (card.hasClass('scrap')) {
            move_to_stack_id = state.stacks[4].id;
        }

        if ((card != null && card_id != -1) && 
            (move_to_stack != null && move_to_stack_id != -1)) {
            animateMove(card, move_to_stack, function() {
                move(card_id, move_to_stack_id);
            });
        }
    }
);

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
        skip();
    }
);

refresh();

// fidget with the cards so the stacks looks messy initially
$('#discarded .card').each(function(index) {
    fidget($(this), FIDGET_DISCARD);    
});

$('#equipment .card').each(function(index) {
    fidget($(this), FIDGET_EQUIPMENT);    
});

$('#you .card').each(function(index) {
    fidget($(this), FIDGET_YOU);    
});