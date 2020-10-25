var obbContentBox = {
    init: function (settings) {
        obbContentBox.config = {
            item: $('#Content'),
            textItem: $('#ContentText'),
            boxItem: $('#ContentBox'),
        };

        $.extend(obbContentBox.config, settings);
        obbContentBox.setup();
    },

    setup: function () {
        obbSocket.on('room:get:page', function (msg) {
            obbSocket.emit('room:get:content', {page: msg.page_id})
        });

        obbSocket.on('room:update:content', function (msg) {
            obbContentBox.config.textItem.html(marked(msg.markdown));
        });

        obbSocket.on('room:update:settings', function (msg) {
            obbContentBox.config.textItem
                .css('height', `${msg.content_draw_height}px`)
                .css('width', `${msg.content_draw_width}px`)

            obbContentBox.updateLayout();
        });

        obbSocket.on('room:get:page', function (msg) {
            obbContentBox.config.textItem
                .css('height', `${msg.height}px`)
                .css('width', `${msg.width}px`)

            obbContentBox.updateLayout();
        });

        obbSocket.on('room:get:content', function (msg) {
            obbContentBox.config.textItem.html(marked(msg.markdown));
        });

        obbContentBox.updateLayout();
    },

    updateLayout: function () {
        let contentSelector = obbContentBox.config.item;
        let contentText = obbContentBox.config.textItem;

        let contentWidth = contentSelector.width();

        let textWidth = contentText.width();
        let textHeight = contentText.height();


        let factorMin = contentWidth / textWidth;

        let translateX = textWidth * (factorMin - 1) / 2;
        let translateY = textHeight * (factorMin - 1) / 2;

        contentText.css('transform',
            'translateX(' + translateX + 'px) ' +
            'translateY(' + translateY + 'px) ' +
            'scale(' + factorMin + ') ');

        contentSelector.height(textHeight * factorMin);

        obbContentBox.config.boxItem.trigger('resize');
    },
}

$(obbSocket).on('socket:ready', function () {
    obbContentBox.init()
});