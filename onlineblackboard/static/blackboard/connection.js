$(document).ready(function () {
    let room_id = $.urlParam('room_id');
    let socket = io.connect('/blackboard');
    $.socket = socket;

    socket.on('connect', function () {
        $('#status').text(room_id);
        socket.emit('join', room_id);
    });
    socket.on('disconnect', function () {
        $('#status').text('Disconnected');
    });

    socket.on('change_room', function (msg) {
        $('#status').text(msg.room_id);
    });
    socket.on('print_content', function (msg) {
        let sel_content = $("#content");
        sel_content.html(marked(msg.markdown));

        sel_content.scrollTop(sel_content.scrollHeight);

    });
});