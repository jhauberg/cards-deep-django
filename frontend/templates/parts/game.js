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

//////////////////
// event hookups

var state = {}

function updateHealth() {
    var new_health_amount = state.health;
    var amount_in_pixels = new_health_amount * 6;

    $('.health-bar').css("width", amount_in_pixels);
    $('.health-ui .value').text(new_health_amount);
}

function determineDiscardVisibility() {
    var discarded_stack_element = $('#discarded');

    if (state.stacks[5].cards.length > 0) {
        discarded_stack_element.css('visibility', 'visible');
    } else {
        discarded_stack_element.css('visibility', 'hidden');
    }
}

function onStateChanged(previous_state) {
    updateHealth();
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

                determineDiscardVisibility();
            },
            'json'
        );
    }
}

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

$("#room .card").mouseup(
    function() {
        var card_id = this.id.replace('card-', '');
        var move_to_stack_id = -1;

        if ($(this).hasClass('weapon')) {
            move_to_stack_id = state.stacks[1].id;
        } else if ($(this).hasClass('monster')) {
            move_to_stack_id = state.stacks[2].id;
        } else if ($(this).hasClass('potion')) {
            move_to_stack_id = state.stacks[2].id;
        } else if ($(this).hasClass('treasure')) {
            move_to_stack_id = state.stacks[3].id;
        } else if ($(this).hasClass('scrap')) {
            move_to_stack_id = state.stacks[4].id;
        }
        
        if (card_id != -1 && move_to_stack_id != -1) {
            var discarded = $('#discarded');
            var discarded_position = discarded.position();

            $(this).unbind('mouseup mouseenter mouseleave');

            $(this).animate({
                left: discarded_position.left,
                top: discarded_position.top
            }, 1000, 'linear', function() {
                $(this).removeAttr('style');
                $(this).removeClass('monster treasure scrap potion weapon');
                $(this).empty();

                fidget($(this), 12);

                discarded.append(this);
                discarded.css('visibility', 'visible');
            });

            $.post("{% url perform_action state.session_id 'move' %}", 
                { 
                    'csrfmiddlewaretoken': '{{ csrf_token }}',
                    'card_id': card_id,
                    'to_stack_id': move_to_stack_id
                },
                function(response) {
                    refresh(response.state);
                },
                'json'
            );
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
);

refresh();

// fidget with the discarded cards so the stack looks messy
$('#discarded .card').each(function(index) {
    fidget($(this), 12);    
});