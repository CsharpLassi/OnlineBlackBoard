var obbAdminUserList = {
    init: function (settings) {
        obbAdminUserList.config = {
            Items: $('#UserList'),
        }
        $.extend(obbAdminUserList.config, settings);

        this.setup();
    },
    setup: function () {
        obbSocket.on('room:join:self', function (msg) {
            obbSocket.emit('room:get:users', {
                roomId: msg.room.base.id,
            })
        });

        obbSocket.on('room:get:users', function (msg) {
            obbAdminUserList.config.Items.empty();
            msg.users.forEach(e =>{
                obbAdminUserList.addUser(e);
            });
        })

        obbSocket.on('room:join:user', function (msg) {
            obbAdminUserList.addUser(msg.user);
        })

        obbSocket.on('room:update:user', function (msg) {
            obbAdminUserList.updateUser(msg.user)
        })

        obbSocket.on('room:leave:user', function (msg) {
            obbAdminUserList.removeUser(msg.sessionId);
        })
    },

    updateUser: function (user) {
        let userId = 'user-' + user.sessionId
        let userDiv = obbAdminUserList.config.Items.children('#' + userId);

        userDiv.children('.allowDraw').prop('checked', user.allowDraw);
        userDiv.children('.allowNewPage').prop('checked', user.allowNewPage);
    },

    removeUser: function (userId) {
        $('tr#user-' + userId).remove()
    },
    addUser: function (user) {
        let userId = 'user-' + user.sessionId
        // Add Item
        obbAdminUserList.config.Items.children('#' + userId).remove();

        obbAdminUserList.config.Items.each(function () {
            let trUser = $('<tr />', {
                id: userId,
            }).appendTo($(this));

            // Id
            $('<td />', {
                text: user.sessionId,
            }).appendTo(trUser);

            // Name
            let tdName = $('<td />', {
                text: user.base.name,
            }).appendTo(trUser);
            if (this.creator)
                tdName.addClass('creator')

            // Mode
            $('<td />', {
                text: user.mode,
            }).appendTo(trUser);

            //Draw
            let allowDrawCheckbox = $('<input />', {
                class: 'allowDraw',
                type: 'checkbox'
            })
                .prop('checked', user.allowDraw)
                .click({user: user}, function (event) {
                    let user = event.data.user;
                    let allowDraw = this.checked;
                    obbSocket.emit('room:update:user', {
                        sessionId: user.sessionId,
                        allowDraw: allowDraw,
                    });
                });
            $('<td />').append(allowDrawCheckbox).appendTo(trUser);

            //Draw
            let allowNewPageCheckbox = $('<input />', {
                class: 'allowNewPage',
                type: 'checkbox'
            })
                .prop('checked', user.allowNewPage)
                .click({user: user}, function (event) {
                    let user = event.data.user;
                    let allowNewPage = this.checked;
                    obbSocket.emit('room:update:user', {
                        sessionId: user.sessionId,
                        allow_new_page: allowNewPage,
                    });
                });
            $('<td />').append(allowNewPageCheckbox).appendTo(trUser);

            //Draw
            let syncCheckbox = $('<input />', {
                class: 'inSync',
                type: 'checkbox'
            })
                .prop('checked', false)
            $('<td />').append(syncCheckbox).appendTo(trUser);
        });
    }
};

$(obbSocket).on('socket:ready', function () {
    obbAdminUserList.init()
});
