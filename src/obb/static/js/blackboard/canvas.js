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

};

var obbSketchContent = {
    sketchCanvases: [],

    init: function (settings) {
        obbSketchContent.config = {
            globalCanvas: $('#ContentSketchpadGlobal'),
            userCanvas: $('#ContentSketchpadUser'),
        };

        $.extend(obbSketchContent.config, settings);

        obbSketchContent.setup();
    },

    setup: function () {
        obbSketchContent.sketchCanvases.push(obbSketchCanvas.init(obbSketchContent.config.globalCanvas, {
            onZ: 3,
        }));
        obbSketchContent.sketchCanvases.push(obbSketchCanvas.init(obbSketchContent.config.userCanvas, {
            onZ: 4,
        }));

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

    setThickness: function (thickness){
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