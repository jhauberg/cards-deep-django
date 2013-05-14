function getState(completed) {
    $.get("{% url state state.session_id %}",
        { },
        completed,
        'json'
    );
}

function move(card, stack, completed) {
    $.post("{% url perform_action state.session_id 'move' %}",
        {
            'csrfmiddlewaretoken': '{{ csrf_token }}',
            'card_id': card,
            'to_stack_id': stack
        },
        completed,
        'json'
    );
}

function skip(completed) {
    $.post("{% url perform_action state.session_id 'skip' %}",
        {
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        completed,
        'json'
    );
}

function clear(stack, completed) {
    $.post("{% url perform_action state.session_id 'clear' %}",
        {
            'csrfmiddlewaretoken': '{{ csrf_token }}',
            'stack_id': stack
        },
        completed,
        'json'
    );
}