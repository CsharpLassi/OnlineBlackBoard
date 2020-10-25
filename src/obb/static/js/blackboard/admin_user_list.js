var obbUserUserPlugin = {

    getAdminClassId: function () {
        return 'user-' + this.user_id;
    },

    getAdminSelector: function () {
        return $('.' + this.getAdminClassId());
    },

    getAdminContent: function () {
        let trUser = $('<tr />', {
            class: this.getAdminClassId(),
        });

        // Id
        $('<td />', {
            text: this.user_id,
        }).appendTo(trUser);

        // Name
        let tdName = $('<td />', {
            text: this.username,
        }).appendTo(trUser);
        if (this.creator)
            tdName.addClass('creator')

        // Mode
        $('<td />', {
            text: this.mode,
        }).appendTo(trUser);

        //Draw
        let allowDrawCheckbox = $('<input />', {
            class: 'allowDraw',
            type: 'checkbox'
        })
            .prop('checked', this.allow_draw)
            .click({user: this}, function (event) {
                let user = event.data.user;
                let allow_draw = this.checked;
                obbSocket.emit('room:update:user', {
                    user_id: user.user_id,
                    allow_draw: allow_draw,
                });
            });
        $('<td />').append(allowDrawCheckbox).appendTo(trUser);

        //Draw
        let allowNewPageCheckbox = $('<input />', {
            class: 'allowNewPage',
            type: 'checkbox'
        })
            .prop('checked', this.allow_new_page)
            .click({user: this}, function (event) {
                let user = event.data.user;
                let allow_new_page = this.checked;
                obbSocket.emit('room:update:user', {
                    user_id: user.user_id,
                    allow_new_page: allow_new_page,
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

        return trUser;
    },

    updateAdminContent: function () {
        let selector = this.getAdminSelector();

        selector.find('.allowDraw').prop('checked', this.allow_draw);
        selector.find('.allowNewPage').prop('checked', this.allow_new_page);
    },

    removeAdminContent: function () {
        let selector = this.getAdminSelector();
        selector.remove();
    }
}

var obbAdminUserList = {
    init: function (settings) {
        obbAdminUserList.config = {
            Items: $('#UserList'),
        }
        $.extend(obbAdminUserList.config, settings);

        this.setup();
    },
    setup: function () {
        obbSocket.on('room:join', function (msg) {
            obbAdminUserList.config.Items.empty()
            $.each(msg.room.users, function (key, item) {
                let user = obbUser.init(item)
                obbAdminUserList.config.Items.append(user.getAdminContent())
            });
        });

        obbSocket.on('room:join:user', function (msg) {
            let user = obbUser.init(msg.user)
            obbAdminUserList.config.Items.append(user.getAdminContent())
        })

        obbSocket.on('room:update:user', function (msg) {
            let user = obbUser.init(msg.user)
            user.updateAdminContent();
        })

        obbSocket.on('room:leave:user', function (msg) {
            let user = obbUser.init(msg.user)
            user.removeAdminContent();
        })
    }
};

$(obbUser).ready(function () {
    $.extend(obbUser, obbUserUserPlugin)
});

$(obbSocket).on('socket:ready', function () {
    obbAdminUserList.init()
});
