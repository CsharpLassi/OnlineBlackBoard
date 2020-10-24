var obbUser = {
    user_id: '',
    username: 'Guest',
    mode: 'blackboard',
    creator: false,
    allow_draw: false,

    init: function (values) {
        let newItem = {}
        $.extend(newItem, obbUser, values);

        return newItem;
    }
}

var obbRoom = {
    room_id: '',
    room_name: '',

    init: function (values) {
        let newItem = {}
        $.extend(newItem, obbRoom, values);
        return newItem;
    }
}

var obbSocket = {
    token: '',
    socket: null,
    connected: false,
    user: null,
    room: null,

    init: function (settings) {
        obbSocket.config = {
            statusItems: $('#status'),
            namespace: '/',
        };

        $.extend(obbSocket.config, settings);
        obbSocket.setup()
    },

    setup: function () {
        obbSocket.token = $('meta[name=session-token]').attr("content");
        obbSocket.config.statusItems.text('Disconnected');

        obbSocket.user = obbUser.init();
        obbSocket.room = obbRoom.init();

        obbSocket.socket = io.connect(this.config.namespace);
        obbSocket.socket.on('connect', function () {
            obbSocket.config.statusItems.text('Connected');

            if (obbSocket.token)
                obbSocket.emit('room:join');
        });

        obbSocket.socket.on('disconnect', function () {
            obbSocket.config.statusItems.text('Disconnected');
        });

        obbSocket.socket.on('room:join', function (msg) {
            obbSocket.user = obbUser.init(msg.user);
            obbSocket.room = obbRoom.init(msg.room);
            $('#status').text(obbSocket.room.room_name + ':' + obbSocket.user.user_id);
        });

        $(this).trigger('socket:ready')
    },

    on: function (event, func) {
        obbSocket.socket.on(event, func);
    },

    emit: function (event, data) {
        if (!data)
            data = {}

        $.extend(data, {token: this.token});
        this.socket.emit(event, data);
    },

    isUser: function (user, defaultValue =false) {
        if (!user)
            return defaultValue;
        return user.user_id === obbSocket.user.user_id;
    }

};