var obbContentBox = {
    init: function (settings) {
        obbContentBox.config = {
            item: $('.PageContent'),

        };

        $.extend(obbContentBox.config, settings);
        obbContentBox.setup();
    },

    setup: function () {
        //Create Content Blocker
        $('<div />', {
            class: 'ContentBlocker',
        }).css('z-index', 2).appendTo(obbContentBox.config.item)

        //ContentText
        $('<div />', {
            class: 'ContentText',
        }).css('z-index', 0).appendTo(obbContentBox.config.item)

        obbSocket.on('room:join:self', function (msg) {
            let room = obbRoom.init(msg.room);
            obbContentBox.updateLayout(room.base.drawHeight, room.base.drawWidth);
            obbContentBox.loadContent();
        });

        obbSocket.on('self:update', function (msg) {
            // Todo: ChangeList
            obbContentBox.loadContent(msg.currentPage);
        });

        obbSocket.on('room:get:content', function (msg) {
            obbContentBox.updateContent(msg.markdown, msg.pageId);
        });

        obbSocket.on('room:update:content', function (msg) {
            obbContentBox.updateContent(msg.markdown, msg.pageId);
        });

        obbSocket.on('room:update', function (msg) {
            let room = obbRoom.init(msg.room);
            obbContentBox.updateLayout(room.base.drawHeight, room.base.drawWidth);
        });

        obbSocket.on('room:update:page', function (msg) {
            let page = msg.page;
            obbContentBox.updateLayout(page.base.drawHeight, page.base.drawWidth, page.base.id);
        });

        obbSocket.on('room:get:page', function (msg) {
            return
        });
    },

    loadContent: function (page_id = null) {
        if (page_id) {
            obbSocket.emit('room:get:content', [
                {
                    page_id: page_id,
                }
            ]);
        }

        let pageIds = [];
        let idMessage = [];
        obbContentBox.config.item.each(function () {
            let dataPage = parseInt($(this).data('pageId'));
            if (!dataPage)
                dataPage = obbSocket.user.currentPage;

            if (!pageIds.includes(dataPage)) {
                pageIds.push(dataPage)
                idMessage.push({
                    page_id: dataPage,
                });
            }
        })

        obbSocket.emit('room:get:content', idMessage);
    },
    updateContent: function (markdown, pageId = null) {
        obbContentBox.config.item.filter(function () {
                let divPageId = $(this).data("pageid")
                return (divPageId === 'current' && (!pageId || pageId === obbSocket.user.currentPage)) || divPageId === pageId;
            }
        ).children('.ContentText').html(marked(markdown))
    },

    updateLayout: function (height, width, pageId = null) {
        obbContentBox.config.item.filter(function () {
                let divPageId = $(this).data("pageid")
                return (divPageId === 'current' && (!pageId || pageId === obbSocket.user.currentPage)) || divPageId === pageId;
            }
        ).children('.ContentText').each(function () {
            let maxWidth = $(this).parent().width();

            let factorMin = maxWidth / width;

            let translateX = width * (factorMin - 1) / 2;
            let translateY = height * (factorMin - 1) / 2;

            $(this).css('width', width + 'px').css('height', height + 'px')
                .css('transform',
                    'translateX(' + translateX + 'px) ' +
                    'translateY(' + translateY + 'px) ' +
                    'scale(' + factorMin + ') ');
            $(this).parent().height(height * factorMin)
        });
    },
}

$(obbSocket).on('socket:ready', function () {
    obbContentBox.init()
});