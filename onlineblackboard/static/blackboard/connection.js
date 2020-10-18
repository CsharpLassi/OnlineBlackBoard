$(document).ready(function () {
    let room_id = $.urlParam('room_id');
    let socket = io.connect('/blackboard');
    $.socket = socket;
    $(document).trigger('socket:ready')

    socket.on('connect', function () {
        $('#status').text('Connected');
    });

    socket.on('disconnect', function () {
        $('#status').text('Disconnected');
    });

    socket.on('room:joined', function (msg) {
        $.user = msg.user
        $('#status').text(msg.room.room_name);
    });


    socket.on('room:created', function (msg) {
        $('#roomList').append(`<li id="room-${msg.room.room_id}" class="nav-item"><a class="nav-link" href="${msg.room_url}">${msg.room.room_name}</a></li>`)
    });

    socket.on('room:closed', function (msg) {
        let room_div_id = `room-${msg.room_id}`
        $('#' + room_div_id).remove()
    });

    socket.on('room:user:joined', function (msg) {
        let user_div_id = `user-${msg.user.user_id}`
        if (!$('#' + user_div_id).length)
            $('#userList').append(`<div id="${user_div_id}">${msg.user.username}</div>`)
    })

    socket.on('user:disconnected', function (msg) {
        let user_div_id = `user-${msg.user_id}`
        $('#' + user_div_id).remove()

    })

    socket.on('user:data:changed', function (msg) {
        let user_div_id = `user-${msg.user_id}`
        $('#' + user_div_id).text(msg.username);

        if (msg.user_id !== $.user.user_id)
            $.user = msg.user_id

    })

    if (room_id !== null) {
        socket.on('room:updated', function (msg) {
            $('#status').text(msg.room_name);
        });
        socket.on('connect', function () {
            socket.emit('room:join', room_id);
        });

        socket.on('room:print', function (msg) {
            let sel_content = $("#content");
            sel_content.html(marked(msg.markdown));

            sel_content.scrollTop(sel_content.scrollHeight);
        });
    }
});