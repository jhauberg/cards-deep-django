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

function toggleVisibility(element) {
    if (element.css('visibility') == 'hidden') {
        element.css('visibility', 'visible');
    } else {
        element.css('visibility', 'hidden');
    }
}

function toggleButton(button, enabled) {
    if (enabled) {
        button.removeClass('disabled');
    } else {
        button.addClass('disabled');
    }
}

jQuery.fn.reverse = [].reverse;