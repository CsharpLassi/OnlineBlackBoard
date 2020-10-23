var obbContentBox = {
    init: function (settings) {
        obbContentBox.config = {
            item: $('#Content'),
            boxItem: $('#ContentBox'),
            textItem: $('#contentText'),
        };

        $.extend(obbContentBox.config, settings);
        obbContentBox.setup();
    },

    setup: function () {
        obbSocket.on('room:update:content', function (msg) {
            obbContentBox.config.textItem.html(marked(msg.markdown));
        });

        this.updateLayout();
    },

    updateLayout: function () {
        let contentSelector = obbContentBox.config.item;
        let contentBox = obbContentBox.config.boxItem;

        let contentWidth = contentSelector.width();
        let contentHeight = contentSelector.height();

        let boxWidth = contentBox.width();
        let boxHeight = contentBox.height();


        let factorX = contentWidth / boxWidth;

        let factorMin = factorX;

        let translateX = boxWidth * (factorMin - 1) / 2;
        let translateY = boxHeight * (factorMin - 1) / 2;

        contentBox.css('transform',
            'translateX(' + translateX + 'px) ' +
            'translateY(' + translateY + 'px) ' +
            'scale(' + factorMin + ') ');

        contentSelector.height(contentHeight * factorMin)
    },
}

$(obbSocket).on('socket:ready', function () {
    obbContentBox.init()
});