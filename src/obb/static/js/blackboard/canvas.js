var obbSketchCanvas = {
    selector: null,
    sketchpad: null,
    mode: 'draw',
    thickness: 2,
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

        this.sketchpad.recordStrokes = this.recordStrokes;
        this.sketchpad.mode = this.mode;
        this.sketchpad.weight = this.thickness;
        this.sketchpad.width = ele.width;
        this.sketchpad.height = ele.height;

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
            obbSocket.emit('room:update:sketch', {stroke: stroke});
        });
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

    draw: function (stroke) {
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

        this.sketchpad.recordStrokes = this.recordStrokes;
        this.sketchpad.mode = this.mode;
    }

};

var obbSketchContent = {
    sketchCanvases: [],
    globalSketchPad: null,
    userSketchPad: null,

    init: function (settings) {
        obbSketchContent.config = {
            globalCanvas: $('#ContentSketchpadGlobal'),
            userCanvas: $('#ContentSketchpadUser'),
        };

        $.extend(obbSketchContent.config, settings);

        obbSketchContent.setup();
    },

    setup: function () {
        obbSketchContent.globalSketchPad = obbSketchCanvas.init(obbSketchContent.config.globalCanvas, {
            onZ: 3,
        });
        obbSketchContent.sketchCanvases.push(obbSketchContent.globalSketchPad);

        obbSketchContent.userSketchPad = obbSketchCanvas.init(obbSketchContent.config.userCanvas, {
            onZ: 4,
        });
        obbSketchContent.sketchCanvases.push(obbSketchContent.userSketchPad);

        obbSocket.on('room:join', function (msg) {
            let user = msg.user;

            obbSocket.emit('room:get:sketch');

            if (user.allow_draw) {
                obbSketchContent.globalSketchPad.changeRecordStroke(true);

                obbSketchContent.globalSketchPad.onZ = 4;
                obbSketchContent.userSketchPad.onZ = 3;
            } else {
                obbSketchContent.globalSketchPad.changeRecordStroke(false);

                obbSketchContent.globalSketchPad.onZ = 3;
                obbSketchContent.userSketchPad.onZ = 4;
            }


            obbSketchContent.showAll();
        });

        obbSocket.on('room:update:user', function (msg) {
            let user = msg.user;

            if (!obbSocket.isUser(user))
                return

            if (user.allow_draw) {
                obbSketchContent.globalSketchPad.changeRecordStroke(true);

                obbSketchContent.globalSketchPad.onZ = 4;
                obbSketchContent.userSketchPad.onZ = 3;
            } else {
                obbSketchContent.globalSketchPad.changeRecordStroke(false);

                obbSketchContent.globalSketchPad.onZ = 3;
                obbSketchContent.userSketchPad.onZ = 4;
            }


            obbSketchContent.showAll();
        });

        obbSocket.on('room:update:sketch', function (msg) {
            let creator = msg.creator;
            if (obbSocket.isUser(creator))
                return

            obbSketchContent.globalSketchPad.draw(msg.stroke);
        });

        obbSocket.on('room:get:sketch', function (msg) {
            msg.strokes.forEach(s => {
                obbSketchContent.globalSketchPad.draw(s);
            });
        });

        obbSketchContent.showAll();
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

    showAll: function () {
        obbSketchContent.sketchCanvases.forEach(e => e.show());
    },

    hideAll: function () {
        obbSketchContent.sketchCanvases.forEach(e => e.hide());
    }
};

var obbSketchToolboxButton = {
    default: true,
    cmd: null,
    group: null,
    onlyOn: false,
    onClasses: ['enabled'],
    offClasses: ['disabled'],
    symbolOnClasses: [],
    symbolOffClasses: [],


    init: function (settings) {
        let item = {}
        $.extend(item, obbSketchToolboxButton, settings);
        item.setup()
    },

    setup: function () {
        if (!this.cmd)
            return

        this.cmd.click({item: this}, function (event) {
            let item = event.data.item;
            item.click()
        });

        if (this.default)
            this.setOn()
        else
            this.setOff()
    },

    click: function () {
        let enabled = this.cmd.hasClass(this.onClasses)

        if (!enabled || this.onlyOn)
            this.setOn()
        else
            this.setOff()
    },

    setOn: function (call = true) {
        if (call)
            this.onClick();

        if (this.group)
            this.group.removeClass(this.onClasses).addClass(this.offClasses);

        this.cmd.addClass(this.onClasses).removeClass(this.offClasses);

        this.cmd.children().addClass(this.symbolOnClasses).removeClass(this.symbolOffClasses);
    },
    setOff: function (call = true) {
        if (call)
            this.offClick();

        if (this.group)
            this.group.addClass(this.onClasses).removeClass(this.offClasses);

        this.cmd.removeClass(this.onClasses).addClass(this.offClasses);

        this.cmd.children().removeClass(this.symbolOnClasses).addClass(this.symbolOffClasses);
    },

    onClick: function () {
    },
    offClick: function () {
    }
}

var obbSketchToolbox = {
    cmdEnable: null,
    cmdModeDraw: null,


    init: function (settings) {
        obbSketchToolbox.config = {};

        $.extend(obbSketchToolbox.config, settings);

        this.setup();
    },

    setup: function () {
        this.cmdEnable = obbSketchToolboxButton.init({
            onClick: obbSketchContent.showAll,
            offClick: obbSketchContent.hideAll,
            cmd: $('#cmdEnableDraw'),
            symbolOnClasses: ['fa-check-square'],
            symbolOffClasses: ['fa-square']
        });

        this.cmdModeDraw = obbSketchToolboxButton.init({
            onClick: obbSketchContent.setDraw,
            default: true,
            onlyOn: true,
            cmd: $('#cmdModeDraw'),
            group: $('.sketchToolboxControl.modeControl')
        });

        this.cmdModeErease = obbSketchToolboxButton.init({
            onClick: obbSketchContent.setErase,
            default: false,
            onlyOn: true,
            cmd: $('#cmdModeEraser'),
            group: $('.sketchToolboxControl.modeControl')
        })

        // Todo: obbSketchToolboxRange
        $('#rangeThickness')
            .attr('value', 2)
            .on('change', function () {
                let thickness = parseFloat(this.value);
                obbSketchContent.setThickness(thickness);
            });
    }
}

$(obbSocket).on('socket:ready', function () {
    obbSketchContent.init();
    obbSketchToolbox.init();
});