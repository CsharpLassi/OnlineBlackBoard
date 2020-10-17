$(document).ready(function () {
    let room_id = $.urlParam('room_id');
    let socket = io.connect('/blackboard');
    $.socket = socket;


    socket.on('connect', function () {
        $('#status').text('Connected');
    });

    socket.on('room_created', function (msg) {
        $('#roomList').append(`<li class="nav-item"><a class="nav-link" href="${msg.room_url}">${msg.room_id}</a></li>`)
    });

    socket.on('disconnect', function () {
        $('#status').text('Disconnected');
    });

    if (room_id !== null) {
        socket.on('change_room', function (msg) {
            $('#status').text(msg.room_id);
        });
        socket.on('connect', function () {
            $('#status').text(room_id);
            socket.emit('join', room_id);
        });

        socket.on('print_content', function (msg) {
            let sel_content = $("#content");
            sel_content.html(marked(msg.markdown));

            sel_content.scrollTop(sel_content.scrollHeight);
        });
    }
});