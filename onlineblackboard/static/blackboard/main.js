$.urlParam = function (name) {
    let results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results === null)
        return null
    return results[1] || null;
}

$(document).ready(function () {
    let div_content = $('#content');

    if(!div_content.length)
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

});