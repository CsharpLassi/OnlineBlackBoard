var oldVal = "";
$(document).ready(function () {
    $("#board").on("change keyup paste", function () {
        var currentVal = $(this).val();
        if (currentVal === oldVal) {
            return; //check to prevent multiple simultaneous triggers
        }
        let room_id = $.urlParam('room_id');

        oldVal = currentVal;
        $.socket.emit('room:update:content', {'text': currentVal, 'room_id': room_id})
    });

    $('form#roomEdit').submit(function (event) {
        let room_id = $.urlParam('room_id');
        $.socket.emit('room:update:settings',
            {
                'room_id': room_id,
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