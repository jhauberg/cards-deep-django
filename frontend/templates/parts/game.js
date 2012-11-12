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

function refresh(newState) {
    if (newState) {
        state = newState;
    } else {
        $.get("{% url state state.session_id %}", 
            { },
            function(response) {
                state = response;
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