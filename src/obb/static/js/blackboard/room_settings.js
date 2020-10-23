var obbRoomSettings = {
    init: function (settings) {
        obbRoomSettings.config = {
            items: $('form#roomEdit'),
        };

        $.extend(obbRoomSettings.config, settings);
        obbRoomSettings.setup();
    },
    setup: function () {
        $('form#roomEdit').submit(function (event) {
            obbSocket.emit('room:update:settings',
                {
                    'form_data': $(this).serializeArray()
                });
            return false;
        });
    }
}

$(obbSocket).on('socket:ready', function () {
    obbRoomSettings.init()
});