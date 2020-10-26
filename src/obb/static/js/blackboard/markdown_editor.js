var obbMarkdownEditor = {
    init: function (settings) {
        obbMarkdownEditor.config = {
            items: $('#MarkdownEditor'),
        };

        $.extend(obbMarkdownEditor.config, settings);
        obbMarkdownEditor.setup();
    },

    setup: function () {
        obbMarkdownEditor.config.items.on("change keyup paste", function () {
            let currentVal = $(this).val();
            obbSocket.emit('room:update:content', {
                room_id: obbSocket.room.base.id,
                page_id: obbSocket.user.currentPage,
                text: currentVal
            })
        });

        obbSocket.on('room:update:content', function (msg) {
            if (obbSocket.user.isUser(msg.creatorId))
                return;

            if (msg.pageId === obbSocket.user.currentPage)
                obbMarkdownEditor.config.items.val(msg.text);
        });

        obbSocket.on('room:get:content', function (msg) {
            if (msg.pageId === obbSocket.user.currentPage)
                obbMarkdownEditor.config.items.val(msg.text);
        });
    },
}

$(obbSocket).on('socket:ready', function () {
    obbMarkdownEditor.init()
});