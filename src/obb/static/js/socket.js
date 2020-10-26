var obbUser = {
    base: {
        name: 'anonymous',
        isAdmin: false
    },
    sessionId: '',
    currentPage: 0,
    mode: 'blackboard',
    allowDraw: false,
    allowNewPage: false,

    init: function (values) {
        let newItem = {}
        $.extend(newItem, obbUser, values);

        return newItem;
    },
    isUser: function (id) {
        return this.sessionId === id;
    }
};

var obbRoom = {
    base: {
        id: null,
        name: null,
        fullName: null,
        drawHeight: null,
        drawWidth: null,
    },


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
    sid: '',
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


        obbSocket.socket = io.connect(this.config.namespace);
        obbSocket.socket.on('connect', function () {
            obbSocket.config.statusItems.text('Connected');
            obbSocket.connected = true;

            let roomId = getUrlParameter('r');
            if (roomId)
                obbSocket.emit('room:join', {
                    roomId: roomId
                });
        });

        obbSocket.socket.on('disconnect', function () {
            obbSocket.connected = false;
            obbSocket.config.statusItems.text('Disconnected');
        });

        obbSocket.on('room:join:self', function (msg) {
            obbSocket.sid = msg.sid;
            obbSocket.room = obbRoom.init(msg.room);
            obbSocket.user = obbUser.init(msg.user);

            // Todo: Check currentPage

            $('#status').text(obbSocket.room.base.name + ':' + obbSocket.user.sessionId);
        });

        obbSocket.on('room:new:page', function (msg) {
            if (!obbSocket.user.currentPage)
                obbSocket.emit('room:moveTo:page', {pageId: msg.page.base.id})
        });

        obbSocket.on('self:update', function (msg) {
            obbSocket.user = obbUser.init(msg);
        });

        $(this).trigger('socket:ready')
    },

    on: function (event, func) {
        obbSocket.socket.on(event, function (msg) {
            if (!msg.success) {
                msg.errors.forEach(e => console.log(e));
                return //Todo: Print Error
            }
            if (!Array.isArray(msg.item))
                func(msg.item);
            else
                msg.item.forEach(e => func(e));
        });
    },

    emit: function (event, data) {
        if (!data)
            data = {}

        this.socket.emit(event, {
            token: this.token,
            item: data,
        });
    },

    isUser: function (user, defaultValue = false) {
        if (!user)
            return defaultValue;
        return user.user_id === obbSocket.user.user_id;
    }

};