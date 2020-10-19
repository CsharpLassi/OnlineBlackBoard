var oldVal = "";
$(document).ready(function () {
    $("#board").on("change keyup paste", function () {
        var currentVal = $(this).val();
        if (currentVal === oldVal)
            return
        let token = $.urlParam('session');

        oldVal = currentVal;
        $.socket.emit('room:update:content', {'token': token, 'raw_text': currentVal})
    });

    $('form#roomEdit').submit(function (event) {
        let token = $.urlParam('session');
        $.socket.emit('room:update:settings',
            {
                'token': token,
                'from_data': $(this).serializeArray()
            });
        return false;
    });

});

$(document).on('socket:ready', function () {
    $.socket.on('room:print', function (msg) {
        if (msg.creator.user_id !== $.user.user_id)
            $("#board").val(msg.text)
    });
});