$(document).ready(function () {
    let parent = $('#content').parent()
    let content_width = $('#content').width();
    let content_height = $('#content').height();

    let factor_x = parent.width() / content_width;
    let factor_y = (screen.height - parent.position().top) / content_height;

    let factor_min = Math.min(factor_x, factor_y)

    let translate_x = content_width * (factor_min - 1) / 2;
    let translate_y = content_height * (factor_min - 1) / 2;

    $('#content').css('transform',
        'translateX(' + translate_x + 'px) ' +
        'translateY(' + translate_y + 'px) ' +
        'scale(' + factor_min + ') ');

});