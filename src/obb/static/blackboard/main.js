function drawContent() {
    let div_content = $('#contentText');

    if (!div_content.length)
        return

    let parent = div_content.parent();
    let content_width = div_content.width();
    let content_height = div_content.height();

    let factor_x = parent.width() / content_width;
    let factor_y = (screen.height - parent.position().top) / content_height;

    let factor_min = Math.min(factor_x, factor_y)

    let translate_x = content_width * (factor_min - 1) / 2;
    let translate_y = content_height * (factor_min - 1) / 2;

    div_content.css('transform',
        'translateX(' + translate_x + 'px) ' +
        'translateY(' + translate_y + 'px) ' +
        'scale(' + factor_min + ') ');
    // Todo: Vielleicht etwas schöner später

    let new_width = content_width * factor_min;
    let new_height = content_height * factor_min;

    $('#content').width(new_width).height(new_height);
    $('.contentSketchpad').attr({'width': new_width, 'height': new_height});

    $('.content-translateY').css('transform', `translateY(${translate_y}px)`);

    $(document).trigger('content:change')
}

$.urlParam = function (name) {
    let results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results === null)
        return null
    return results[1] || null;
}

$(document).on('socket:ready', function (socket) {
    $.socket.on('room:updated:settings', function (data) {
        $('#contentText')
            .css('height', `${data.content_draw_height}px`)
            .css('width', `${data.content_draw_width}px`)
        drawContent();
    });
});


$(document).ready(function () {
    drawContent();
});