$(document).ready(function () {

    let socket = io.connect('/blackboard');
    $.socket = socket;
    $(document).trigger('socket:ready', socket)

    socket.on('connect', function () {
        $('#status').text('Connected');

        let session_token = $.urlParam('session');
        if (session_token)
            socket.emit('room:join', {token: session_token});
    });

    socket.on('disconnect', function () {
        $('#status').text('Disconnected');
    });

    socket.on('room:joined', function (msg) {
        $.user = msg.user
        $('#status').text(msg.room.room_name);
    });


    socket.on('room:user:joined', function (msg) {
        let user_div_id = `user-${msg.user.user_id}`
        if (!$('#' + user_div_id).length)
            $('#userList').append(`<div id="${user_div_id}">${msg.user.username}</div>`)
    });

    socket.on('room:user:leave', function (msg) {
        let user_div_id = `user-${msg.user.user_id}`
        $('#' + user_div_id).remove()

    });

    socket.on('room:print', function (msg) {
        let sel_content = $("#contentText");
        sel_content.html(marked(msg.markdown));

        sel_content.scrollTop(sel_content.scrollHeight);
    });


});