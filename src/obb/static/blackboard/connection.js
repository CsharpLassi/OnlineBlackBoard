$(document).ready(function () {

    let socket = io.connect('/blackboard');
    let token = $('meta[name=session-token]').attr("content");
    $.socket = socket;
    $(document).trigger('socket:ready', socket)

    socket.on('connect', function () {
        $('#status').text('Connected');

        if (token)
            socket.emit('room:join', {token: token});
    });

    socket.on('disconnect', function () {
        $('#status').text('Disconnected');
    });

    socket.on('room:joined', function (msg) {
        $.user = msg.user
        $('#status').text(msg.room.room_name + ':' + msg.user.user_id);

        socket.emit('room:get:content', {token: token});
    });


    socket.on('room:user:joined', function (msg) {
    });

    socket.on('room:user:leave', function (msg) {
    });

    socket.on('room:print', function (msg) {
        let sel_content = $("#contentText");
        sel_content.html(marked(msg.markdown));

        sel_content.scrollTop(sel_content.scrollHeight);
    });


});