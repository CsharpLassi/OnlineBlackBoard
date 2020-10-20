function addUser(user) {
    let user_div_id = `user-${user.user_id}`
    $('#' + user_div_id).remove()
    {
        let user_element = $('<tr />', {
            id: user_div_id
        });

        // Id
        $('<td />', {
            text: user.user_id,
        }).appendTo(user_element);

        // Name
        let td_name = $('<td />', {
            text: user.username,
        }).appendTo(user_element);
        if (user.creator)
            td_name.css('color','red');

        // Mode
        $('<td />', {
            text: user.mode,
        }).appendTo(user_element);

        //Draw
        let draw_checkbox = $('<input />', {
            id: 'user-' + user.user_id + '-allow-draw',
            type: 'checkbox'
        });
        draw_checkbox.prop('checked', user.allow_draw);
        draw_checkbox.click(function () {
            let token = $('meta[name=session-token]').attr("content");
            $.socket.emit('room:update:user', {
                token: token,
                user_id: user.user_id,
                allow_draw: this.checked,
            })
        });

        $('<td />').append(draw_checkbox).appendTo(user_element);

        user_element.appendTo('#userList')
    }


}


$(document).ready(function () {

    let token = $('meta[name=session-token]').attr("content");
    let oldVal = "";

    $("#board").on("change keyup paste", function () {
        var currentVal = $(this).val();
        if (currentVal === oldVal)
            return

        oldVal = currentVal;
        $.socket.emit('room:update:content', {'token': token, 'raw_text': currentVal})
    });

    $('form#roomEdit').submit(function (event) {
        $.socket.emit('room:update:settings',
            {
                'token': token,
                'from_data': $(this).serializeArray()
            });
        return false;
    });

});

$(document).on('socket:ready', function () {
    $.socket.on('room:joined', function (msg) {
        $('#userList').empty()
        $.each(msg.room.users, function (key, item) {
            addUser(item);
        });
    });

    $.socket.on('room:updated:user', function (msg) {
        let user = msg.user
        $('#user-' + user.user_id + '-allow-draw').prop('checked', user.allow_draw)
    });

    $.socket.on('room:user:joined', function (msg) {
        addUser(msg.user)
    });

    $.socket.on('room:user:leave', function (msg) {
        let user_div_id = `user-${msg.user.user_id}`
        $('#' + user_div_id).remove()

    });

    $.socket.on('room:print', function (msg) {
        if (msg.creator.user_id !== $.user.user_id)
            $("#board").val(msg.text)
    });


});