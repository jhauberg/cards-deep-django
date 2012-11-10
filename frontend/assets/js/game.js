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
        selectMap(true);
    }
);

$("#map").mouseleave(
    function() {
        selectMap(false);
    }
);