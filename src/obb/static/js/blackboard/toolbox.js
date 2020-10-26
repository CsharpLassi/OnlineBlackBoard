var obbSketchToolboxButton = {
    default: true,
    cmd: null,
    group: null,
    groupOn: true,
    groupOff: true,
    onlyOn: false,
    onClasses: ['enabled'],
    offClasses: ['disabled'],
    symbolOnClasses: [],
    symbolOffClasses: [],
    value: null,

    init: function (settings) {
        let item = {}
        $.extend(item, obbSketchToolboxButton, settings);
        item.setup()

        return item;
    },

    setup: function () {
        if (!this.cmd)
            return

        this.cmd.click({item: this}, function (event) {
            let item = event.data.item;
            item.click()
        });

        if (this.default)
            this.setOn(false)
        else
            this.setOff(false)
    },

    click: function () {
        let enabled = this.cmd.hasClass(this.onClasses)

        if (!enabled || this.onlyOn)
            this.setOn()
        else
            this.setOff()
    },

    setOn: function (call = true) {
        if (call) {
            if (!this.checkOnClick())
                return
            this.onClick()
        }

        if (this.group && this.groupOff)
            this.group.removeClass(this.onClasses).addClass(this.offClasses);

        this.cmd.addClass(this.onClasses).removeClass(this.offClasses);

        this.cmd.children().addClass(this.symbolOnClasses).removeClass(this.symbolOffClasses);
    },
    setOff: function (call = true) {
        if (call)
            this.offClick();

        if (this.group && this.groupOn)
            this.group.addClass(this.onClasses).removeClass(this.offClasses);

        this.cmd.removeClass(this.onClasses).addClass(this.offClasses);

        this.cmd.children().removeClass(this.symbolOnClasses).addClass(this.symbolOffClasses);
    },

    checkOnClick: function () {
        return true
    },

    onClick: function () {
    },
    offClick: function () {
    },

    disable: function () {
        this.setEnable(false);
    },
    enable: function () {
        this.setEnable(true);
    },

    setEnable: function (val) {
        this.cmd.prop('disabled', !val);
    },
}

var obbToolBox = {
    init: function (settings) {
        obbToolBox.config = {
            item: $('.ContentToolBox')
        }

        $.extend(obbToolBox.config, settings);

        obbToolBox.setup();
    },

    setup: function () {
        obbToolBox.create();
    },

    create: function () {
        obbToolBox.config.item.each(function () {
            let forId = $(this).data('for')
            if (!forId)
                return

            forId = '#' + forId;

            $(this).addClass('row');

            let leftDiv = $('<div class="col-auto">').appendTo($(this));
            let mainDiv = $('<div class="col-auto justify-content-center">').appendTo($(this));
            let divUserModeControl = $('<div class="col-auto sketchToolboxControl userModeControl">').appendTo($(this))
            let paddingDiv = $('<div class="col">').appendTo($(this));
            let rightDiv = $('<div class="col-auto">').appendTo($(this));

            let cmdMoveToLeftPage = obbSketchToolboxButton.init({
                onClick: function () {
                    obbSocket.emit('room:moveTo:page', {
                        pageId: cmdMoveToLeftPage.value,

                    })
                },
                onlyOn: true,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl',
                }).append('<i class="fas fa-arrow-left"></i>').appendTo(leftDiv),
            });
            cmdMoveToLeftPage.disable();


            let cmdCreateRightPage = obbSketchToolboxButton.init({
                onClick: function () {
                    obbSocket.emit('room:create:page', {
                        roomId: obbSocket.room.base.id,
                        parent_page_id: cmdCreateRightPage.value,
                        direction: 'right',
                        moveTo: true,
                    })
                },
                onlyOn: true,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl',
                }).append('<i class="fas fa-plus"></i>').appendTo(rightDiv),
            });
            cmdCreateRightPage.disable()

            let cmdMoveToRightPage = obbSketchToolboxButton.init({
                onClick: function () {
                    obbSocket.emit('room:moveTo:page', {
                        pageId: cmdMoveToRightPage.value,
                    })
                },
                onlyOn: true,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl',
                }).append('<i class="fas fa-arrow-right"></i>').appendTo(rightDiv),
            });
            cmdMoveToRightPage.disable()


            let cmdDrawMode = obbSketchToolboxButton.init({
                onClick: function () {
                    obbContentSketchCanvas.show(forId);
                    obbContentSketchCanvas.setDrawMode('draw', forId);
                },
                offClick: function () {
                    obbContentSketchCanvas.hide(forId);
                },
                default: false,
                group: $('.sketchToolboxControl.modeControl'),
                groupOn: false,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl modeControl',
                }).append('<i class="fas fa-pen"></i>').appendTo(mainDiv)
            });

            $('<button />', {
                class: 'btn sketchToolboxControl',
            }).colorPick({
                'initialColor': '#000000',
                'pos': 'top',
                'onColorSelected': function () {
                    this.element.css({'backgroundColor': this.color, 'color': this.color});
                    obbContentSketchCanvas.setColor(this.color, forId);
                }
            }).appendTo(mainDiv);

            let cmdEraseMode = obbSketchToolboxButton.init({
                onClick: function () {
                    obbContentSketchCanvas.show(forId);
                    obbContentSketchCanvas.setDrawMode('erase', forId);
                },
                offClick: function () {
                    obbContentSketchCanvas.hide(forId);
                },
                default: false,
                group: $('.sketchToolboxControl.modeControl'),
                groupOn: false,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl modeControl',
                }).append('<i class="fas fa-eraser"></i>').appendTo(mainDiv),
            });

            obbSketchToolboxButton.init({
                onClick: function () {
                    obbContentSketchCanvas.clear(forId);
                },
                onlyOn: true,
                default: true,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl',
                }).append('<i class="fas fa-bacon"></i>').appendTo(divUserModeControl),
            });

            let cmdChangeMode = obbSketchToolboxButton.init({
                onClick: function () {
                    obbContentSketchCanvas.changeMode('global', forId)

                    cmdDrawMode.setOff()
                    cmdEraseMode.setOff()

                    divUserModeControl.addClass('globalMode');
                },
                offClick: function () {
                    obbContentSketchCanvas.changeMode('user', forId)

                    cmdDrawMode.setOff()
                    cmdEraseMode.setOff()

                    divUserModeControl.removeClass('globalMode');
                },
                default: false,
                cmd: $('<button />', {
                    class: 'btn sketchToolboxControl',
                }).append('<i class="fas fa-chalkboard-teacher"></i>').appendTo(divUserModeControl)
            });
            cmdChangeMode.disable();

            $('<input />', {
                type: 'range',
                min: 1,
                max: 20,
                value: 2,
                step: 0.1,
            }).attr('value', 2).on('change', function () {
                let weight = parseFloat(this.value);
                obbContentSketchCanvas.setWeight(weight, forId)
            }).appendTo(mainDiv);

            // socket
            obbSocket.on('room:join:self', function (msg) {
                cmdCreateRightPage.enable(msg.user.allowNewPage)
                cmdCreateRightPage.value = obbSocket.user.currentPage

                cmdChangeMode.setEnable(msg.user.allowDraw);

                obbSocket.emit('room:get:page', {
                    pageId: obbSocket.user.currentPage
                });
            });

            obbSocket.on('self:update', function (msg) {
                cmdCreateRightPage.enable(msg.user.allowNewPage)
                cmdCreateRightPage.value = obbSocket.user.currentPage

                cmdChangeMode.setEnable(msg.user.allowDraw);

                obbSocket.emit('room:get:page', {
                    pageId: obbSocket.user.currentPage
                });
            });

            obbSocket.on('room:get:page', function (msg) {
                let page = msg.page;

                cmdMoveToLeftPage.value = page.base.leftPageId;
                cmdMoveToRightPage.value = page.base.rightPageId;

                cmdMoveToLeftPage.setEnable(page.base.leftPageId != null);
                cmdMoveToRightPage.setEnable(page.base.rightPageId != null);
            });

        });


    }
};

$(obbSocket).on('socket:ready', function () {
    obbToolBox.init()
});