var obbRoomSettings = {
    init: function (settings) {
        obbRoomSettings.config = {
            items: $('form#roomEdit'),
        };

        $.extend(obbRoomSettings.config, settings);
        obbRoomSettings.setup();
    },
    setup: function () {
        obbSocket.on('room:update', function (msg) {
            let room = obbRoom.init(msg.room);
            // Todo: set
        });

        obbRoomSettings.config.items.submit(function (event) {
            obbSocket.emit('room:update',
                {
                    room_id: obbSocket.room.base.id,
                    data: $(this).serializeArray(),
                    page_id: obbSocket.user.currentPage,
                });
            return false;
        });
    }
}

$(obbSocket).on('socket:ready', function () {
    obbRoomSettings.init()
});