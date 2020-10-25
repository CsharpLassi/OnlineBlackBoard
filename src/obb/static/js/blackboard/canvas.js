var obbSketchCanvas = {
    selector: null,
    sketchpad: null,
    mode: 'draw',
    thickness: 2,
    color: '#000000',
    recordStrokes: false,
    onZ: 3,
    offZ: 1,

    init: function (ele, settings) {
        obbSketchCanvas.config = {
            contentParent: $('#ContentBox'),
        }

        let item = {}
        $.extend(item, obbSketchCanvas, settings);

        item.setup(ele);
        return item
    },

    setup: function (ele) {
        this.selector = ele.first();
        this.sketchpad = new Atrament(document.querySelector('#' + this.selector[0].id));

        this.sketchpad.width = ele.width;
        this.sketchpad.height = ele.height;

        this.setAllValues();

        this.hide();

        this.config.contentParent.resize({item: this}, function (event) {
            let item = event.data.item;
            let sel = $(this)

            let new_width = sel.width();
            let new_height = sel.height();

            item.sketchpad.width = new_width;
            item.sketchpad.height = new_height;

            item.selector.attr({'width': new_width, 'height': new_height});
        });


        this.sketchpad.addEventListener('strokerecorded', ({stroke}) => {
            for (let i = 0; i < stroke.points.length; i++) {
                stroke.points[i].x /= this.sketchpad.width
                stroke.points[i].y /= this.sketchpad.height
            }

            obbSocket.emit('room:update:sketch', {page_id: obbSocket.current_page.page_id, stroke: stroke});
        });
    },

    setAllValues: function () {
        this.sketchpad.recordStrokes = this.recordStrokes;
        this.sketchpad.mode = this.mode;
        this.sketchpad.weight = this.thickness;
        this.sketchpad.color = this.color;
    },

    changeColor: function (color = '#000000') {
        this.sketchpad.color = this.color = color;
    },

    changeThickness: function (thickness) {
        this.thickness = thickness;
        this.sketchpad.weight = thickness;
    },

    changeMode: function (mode = 'draw') {
        this.mode = mode;
        this.sketchpad.mode = mode;
    },

    changeRecordStroke: function (record) {
        if (!record)
            record = !this.recordStrokes;

        this.recordStrokes = record;
        this.sketchpad.recordStrokes = this.recordStrokes;
    },

    hide: function () {
        this.selector.css('z-index', this.offZ)
    },

    show: function () {
        this.selector.css('z-index', this.onZ)
    },

    clear: function () {
        this.sketchpad.clear();
    },

    draw: function (stroke) {
        this.sketchpad.recordStrokes = false;

        this.sketchpad.mode = stroke.mode;
        this.sketchpad.weight = stroke.weight;
        this.sketchpad.smoothing = stroke.smoothing;
        this.sketchpad.color = stroke.color;
        this.sketchpad.adaptiveStroke = stroke.adaptiveStroke;

        // don't want to modify original data
        const points = stroke.points.slice();

        let firstPoint = points.shift();
        firstPoint.x *= this.sketchpad.width;
        firstPoint.y *= this.sketchpad.height;
        // beginStroke moves the "pen" to the given position and starts the path
        this.sketchpad.beginStroke(firstPoint.x, firstPoint.y);

        let prevPoint = firstPoint;
        while (points.length > 0) {
            let point = points.shift();
            point.x *= this.sketchpad.width;
            point.y *= this.sketchpad.height;

            // the `draw` method accepts the current real coordinates
            // (i. e. actual cursor position), and the previous processed (filtered)
            // position. It returns an object with the current processed position.
            const {x, y} = this.sketchpad.draw(point.x, point.y, prevPoint.x, prevPoint.y);

            // the processed position is the one where the line is actually drawn to
            // so we have to store it and pass it to `draw` in the next step
            prevPoint = {x, y};
        }

        // endStroke closes the path
        this.sketchpad.endStroke(prevPoint.x, prevPoint.y);

        this.setAllValues();
    }

};

var obbSketchContent = {
    sketchCanvases: [],
    globalSketchPad: null,
    userSketchPad: null,

    mode: 'user',

    init: function (settings) {
        obbSketchContent.config = {
            globalCanvas: $('#ContentSketchpadGlobal'),
            userCanvas: $('#ContentSketchpadUser'),
        };

        $.extend(obbSketchContent.config, settings);

        obbSketchContent.setup();
    },

    setup: function () {
        obbSketchContent.globalSketchPad = obbSketchCanvas.init(obbSketchContent.config.globalCanvas);
        obbSketchContent.sketchCanvases.push(obbSketchContent.globalSketchPad);

        obbSketchContent.userSketchPad = obbSketchCanvas.init(obbSketchContent.config.userCanvas);
        obbSketchContent.sketchCanvases.push(obbSketchContent.userSketchPad);

        obbSocket.on('room:join', function (msg) {

        });

        obbSocket.on('room:get:page', function (msg) {
            obbSocket.emit('room:get:sketch', {page: msg.page_id});
        });

        obbSocket.on('room:update:user', function (msg) {
            let user = msg.user;

            if (!obbSocket.isUser(user))
                return
            return;
        });

        obbSocket.on('room:update:sketch', function (msg) {
            let creator = msg.creator;
            if (obbSocket.isUser(creator))
                return

            if (obbSocket.current_page.page_id !== msg.page_id)
                return

            obbSketchContent.globalSketchPad.draw(msg.stroke);
        });

        obbSocket.on('room:clear:sketch', function (msg) {
            let creator = msg.creator;
            if (obbSocket.isUser(creator))
                return

            obbSketchContent.globalSketchPad.clear();
        });

        obbSocket.on('room:get:sketch', function (msg) {
            obbSketchContent.globalSketchPad.clear()
            msg.strokes.forEach(s => {
                obbSketchContent.globalSketchPad.draw(s);
            });
        });
    },

    setDraw: function () {
        obbSketchContent.setMode('draw')
    },

    setErase: function () {
        obbSketchContent.setMode('erase')
    },

    setMode: function (mode) {
        obbSketchContent.sketchCanvases.forEach(e => e.changeMode(mode));
    },

    setThickness: function (thickness) {
        obbSketchContent.sketchCanvases.forEach(e => e.changeThickness(thickness));
    },

    setColor: function (color) {
        obbSketchContent.sketchCanvases.forEach(e => e.changeColor(color));
    },

    changeModeToGlobal: function () {
        obbSketchContent.mode = 'global'
    },

    changeModeToUser: function () {
        obbSketchContent.mode = 'user'
    },

    show: function () {
        if (obbSketchContent.mode === 'global') {
            obbSketchContent.globalSketchPad.show()
        } else {
            obbSketchContent.userSketchPad.show()
        }

    },

    clear: function () {
        if (obbSketchContent.mode === 'global') {
            obbSketchContent.globalSketchPad.clear();
            obbSocket.emit('room:clear:sketch');
        } else {
            obbSketchContent.userSketchPad.clear();
        }
    },

    hide: function () {
        obbSketchContent.sketchCanvases.forEach(e => e.hide());
    }
};

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

var obbSketchToolbox = {
    cmdGetLeftPage: null,
    cmdGetRightPage: null,
    cmdCreateRightPage: null,
    cmdModeDraw: null,
    cmdChangeMode: null,

    cmdClear: null,

    init: function (settings) {
        obbSketchToolbox.config = {};

        $.extend(obbSketchToolbox.config, settings);

        this.setup();
    },

    setup: function () {
        obbSketchToolbox.cmdGetLeftPage = obbSketchToolboxButton.init({
            onClick: function () {
                obbSocket.emit('room:get:page:left')
            },
            onlyOn: true,
            cmd: $('#cmdGetLeftPage'),
        });
        obbSketchToolbox.cmdGetLeftPage.disable();

        obbSketchToolbox.cmdGetRightPage = obbSketchToolboxButton.init({
            onClick: function () {
                obbSocket.emit('room:get:page:right')
            },
            onlyOn: true,
            cmd: $('#cmdGetRightPage'),
        });
        obbSketchToolbox.cmdGetRightPage.disable()

        obbSketchToolbox.cmdCreateRightPage = obbSketchToolboxButton.init({
            onClick: function () {
                obbSocket.emit('room:get:page:right', {insert: true})
            },
            onlyOn: true,
            cmd: $('#cmdCreateRightPage'),
        });
        obbSketchToolbox.cmdCreateRightPage.disable()


        obbSketchToolbox.cmdModeDraw = obbSketchToolboxButton.init({
            onClick: function () {
                obbSketchContent.show();
                obbSketchContent.setDraw();
            },
            offClick: obbSketchContent.hide,
            default: false,
            cmd: $('#cmdModeDraw'),
            group: $('.sketchToolboxControl.modeControl'),
            groupOn: false,
        });

        obbSketchToolbox.cmdModeErease = obbSketchToolboxButton.init({
            onClick: function () {
                obbSketchContent.show();
                obbSketchContent.setErase();
            },
            offClick: obbSketchContent.hide,
            default: false,
            cmd: $('#cmdModeEraser'),
            group: $('.sketchToolboxControl.modeControl'),
            groupOn: false,
        });

        // Todo: obbSketchToolboxRange
        $('#rangeThickness')
            .attr('value', 2)
            .on('change', function () {
                let thickness = parseFloat(this.value);
                obbSketchContent.setThickness(thickness);
            });

        // Todo: obbSketchToolBoxColorPicker
        $('#cmdChangeColor').colorPick({
            'initialColor': '#000000',
            'pos': 'top',
            'onColorSelected': function () {
                this.element.css({'backgroundColor': this.color, 'color': this.color});
                obbSketchContent.setColor(this.color);
            }
        });

        obbSketchToolbox.cmdcmdClear = obbSketchToolboxButton.init({
            onClick: function () {
                obbSketchContent.clear()
            },
            onlyOn: true,
            default: true,
            cmd: $('#cmdClear'),
        });

        obbSketchToolbox.cmdChangeMode = obbSketchToolboxButton.init({
            onClick: function () {
                obbSketchContent.changeModeToGlobal();

                obbSketchToolbox.cmdModeDraw.setOff();
                obbSketchToolbox.cmdModeErease.setOff();
                $('.sketchToolboxControl.userModeControl').addClass('globalMode');
            },
            offClick: function () {
                obbSketchContent.changeModeToUser()

                obbSketchToolbox.cmdModeDraw.setOff();
                obbSketchToolbox.cmdModeErease.setOff();
                $('.sketchToolboxControl.userModeControl').removeClass('globalMode');
            },
            default: false,
            cmd: $('#cmdChangeMode'),
            groupOn: false,
        });


        // socket
        obbSocket.on('room:get:page', function (msg) {
            obbSketchToolbox.cmdGetLeftPage.setEnable(msg.has_left_page);
            obbSketchToolbox.cmdGetRightPage.setEnable(msg.has_right_page);
        });

        obbSocket.on('room:join', function (msg) {
            obbSketchToolbox.cmdCreateRightPage.setEnable(msg.user.allow_new_page);
            if (msg.user.mode === 'blackboard') {
                $('.sketchToolboxControl svg').addClass('fa-2x')
                $('.colorPickSelector').addClass('fa-2x');
            }

            obbSketchToolbox.cmdChangeMode.setEnable(msg.user.allow_draw);
            obbSketchContent.globalSketchPad.changeRecordStroke(msg.user.allow_draw)
        });

        obbSocket.on('disconnect', function () {
            obbSketchToolbox.cmdChangeMode.setEnable(false);
            obbSketchToolbox.cmdChangeMode.setOff();

            obbSketchContent.globalSketchPad.changeRecordStroke(false)
        });

        obbSocket.on('room:update:user', function (msg) {
            if (!obbSocket.isUser(msg.user))
                return

            obbSketchToolbox.cmdChangeMode.setEnable(msg.user.allow_draw);
            if (!msg.user.allow_draw)
                obbSketchToolbox.cmdChangeMode.setOff();

            obbSketchToolbox.cmdCreateRightPage.setEnable(msg.user.allow_new_page);
            obbSketchContent.globalSketchPad.changeRecordStroke(msg.user.allow_draw)
        });
    }
}

$(obbSocket).on('socket:ready', function () {
    obbSketchContent.init();
    obbSketchToolbox.init();
});