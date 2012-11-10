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

function refresh() {
    $.get("{% url state state.session_id %}", 
        { },
        function(response) {
            state = response;
        },
        'json'
    );
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
                refresh();
            },
            'json'
        );
    }
);

refresh();