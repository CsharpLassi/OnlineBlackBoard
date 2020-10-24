var obbMarkdownEditor = {
    currentValue: '',

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
            if (currentVal === obbMarkdownEditor.currentValue)
                return

            obbMarkdownEditor.currentValue = currentVal;
            obbSocket.emit('room:update:content', {'raw_text': currentVal})
        });

        obbSocket.on('room:update:content', function (msg) {
            let creator = obbUser.init(msg.creator);
            if (!obbSocket.isUser(creator)) {
                obbMarkdownEditor.config.items.val(msg.raw_text);
            }

        });
    },
}

$(obbSocket).on('socket:ready', function () {
    obbMarkdownEditor.init()
});