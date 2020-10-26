var obbContentSketchCanvas = {
    canvasCount: 0,
    init: function (settings) {
        obbContentSketchCanvas.config = {
            item: $('.PageContent'),
            offZ: 1,
            onZ: 3,
        };

        $.extend(obbContentSketchCanvas.config, settings);
        obbContentSketchCanvas.setup();
    },
    setup: function () {
        obbContentSketchCanvas.config.item.each(function () {
            // User
            obbContentSketchCanvas.addCanvas('user', $(this))

            // Global
            obbContentSketchCanvas.addCanvas('global', $(this))

            $(this).data('mode', 'user');
        });

        obbSocket.on('room:join:self', function (msg) {
            obbContentSketchCanvas.loadSketch();
        });

        obbSocket.on('self:update', function (msg) {
            // Todo: ChangeList
            obbContentSketchCanvas.loadSketch(msg.currentPage);
        });

        obbSocket.on('room:get:sketch', function (msg) {
            msg.strokes.forEach(stroke => {
                obbContentSketchCanvas.updateSketch(stroke, msg.pageId);
            });
        });

        obbSocket.on('room:add:sketch', function (msg) {
            obbContentSketchCanvas.updateSketch(msg.stroke, msg.pageId);
        });
    },

    loadSketch: function (page_id = null) {
        if (page_id) {
            obbSocket.emit('room:get:sketch', [
                {
                    page_id: page_id,
                }
            ]);
        }

        let pageIds = [];
        let idMessage = [];
        obbContentSketchCanvas.config.item.each(function () {
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

        obbSocket.emit('room:get:sketch', idMessage);
    },
    updateSketch: function (stroke, pageId = null) {
        obbContentBox.config.item.filter(function () {
                let divPageId = $(this).data("pageid")
                return (divPageId === 'current' && (!pageId || pageId === obbSocket.user.currentPage)) || divPageId === pageId;
            }
        ).each(function () {
            let mode = 'global'
            $(this).children('.contentSketchpad').filter('.' + mode).each(function () {
                let atrament = $(this).data('atrament')

                let oldValues = {
                    recordStrokes: atrament.recordStrokes,
                    mode: atrament.mode,
                    weight: atrament.weight,
                    smoothing: atrament.smoothing,
                    color: atrament.color,
                    adaptiveStroke: atrament.adaptiveStroke,
                }

                atrament.recordStrokes = false;

                atrament.mode = stroke.mode;
                atrament.weight = stroke.weight;
                atrament.smoothing = stroke.smoothing;
                atrament.color = stroke.color;
                atrament.adaptiveStroke = stroke.adaptiveStroke;

                const points = stroke.points.slice();

                let firstPoint = points.shift();
                firstPoint.x *= atrament.width;
                firstPoint.y *= atrament.height;

                atrament.beginStroke(firstPoint.x, firstPoint.y);

                let prevPoint = firstPoint;
                while (points.length > 0) {
                    let point = points.shift();
                    point.x *= atrament.width;
                    point.y *= atrament.height;


                    const {x, y} = atrament.draw(point.x, point.y, prevPoint.x, prevPoint.y);

                    prevPoint = {x, y};
                }

                atrament.endStroke(prevPoint.x, prevPoint.y);

                atrament.recordStrokes = oldValues.recordStrokes;
                atrament.mode = oldValues.mode;
                atrament.weight = oldValues.weight;
                atrament.smoothing = oldValues.smoothing;
                atrament.color = oldValues.color;
                atrament.adaptiveStroke = oldValues.adaptiveStroke;

            });
        })
    },
    addCanvas: function (mode, control) {

        let id = 'sketchCanvas-' + obbContentSketchCanvas.canvasCount;
        obbContentSketchCanvas.canvasCount += 1

        let canvas = $('<canvas />', {
            id: id,
            class: 'contentSketchpad ' + mode,
        }).css('z-index', obbContentSketchCanvas.config.offZ)
            .attr('width', '10px').attr('height', '10px')
            .data('mode', {mode})
            .appendTo(control)

        let atrament = new Atrament(canvas[0], {
            color: '#000000',
            weight: 2,
            mode: 'draw',
            recordStrokes: false,
        });

        canvas.data('atrament', atrament);

        control.on('resize', function (event) {
            let height = $(this).height();
            let width = $(this).width()

            atrament.height = height;
            atrament.width = width;

            canvas.attr('width', width + 'px').attr('height', height + 'px');

        });

        atrament.addEventListener('strokerecorded', ({stroke}) => {
            for (let i = 0; i < stroke.points.length; i++) {
                stroke.points[i].x /= atrament.width
                stroke.points[i].y /= atrament.height
            }

            obbSocket.emit('room:add:sketch',
                {
                    roomId: obbSocket.room.base.id,
                    pageId: obbSocket.user.currentPage,
                    mode: mode,
                    stroke: stroke,
                });
        });
    },
    hide: function (selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            $(this).children('.contentSketchpad').each(function () {
                let atrament = $(this).data('atrament')
                atrament.recordStrokes = false;

                $(this).css('z-index', obbContentSketchCanvas.config.offZ);
            });
        });
    },
    show: function (selector = '*') {

        obbContentSketchCanvas.hide(selector);
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            let mode = $(this).data('mode')
            $(this).children('.contentSketchpad').filter('.' + mode).each(function () {
                let atrament = $(this).data('atrament')
                atrament.recordStrokes = true;

                $(this).css('z-index', obbContentSketchCanvas.config.onZ);
            });
        });

    },

    clear: function (selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            let mode = $(this).data('mode')
            $(this).children('.contentSketchpad').filter('.' + mode).each(function () {
                let atrament = $(this).data('atrament')
                atrament.clear()
            });
        });


    },

    changeMode: function (mode, selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            $(this).data('mode', mode)
        });
    },

    setDrawMode: function (drawMode, selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            $(this).children('.contentSketchpad').each(function () {
                let atrament = $(this).data('atrament')
                atrament.mode = drawMode;
            });
        });


    },
    setColor: function (color, selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            $(this).children('.contentSketchpad').each(function () {
                let atrament = $(this).data('atrament')
                atrament.color = color;
            });
        });


    },
    setWeight: function (weight, selector = '*') {
        obbContentSketchCanvas.config.item.filter(selector).each(function () {
            $(this).children('.contentSketchpad').each(function () {
                let atrament = $(this).data('atrament')
                atrament.weight = weight;
            });
        });


    },
};

$(obbSocket).on('socket:ready', function () {
    obbContentSketchCanvas.init();
});

/*
var obbSketchCanvas = {

    setup: function (ele) {
        this.selector = ele.first();
        this.sketchpad = new Atrament(document.querySelector('#' + this.selector[0].id));


        this.setAllValues();

        this.hide();

        this.sketchpad.addEventListener('strokerecorded', ({stroke}) => {
            for (let i = 0; i < stroke.points.length; i++) {
                stroke.points[i].x /= this.sketchpad.width
                stroke.points[i].y /= this.sketchpad.height
            }

            obbSocket.emit('room:update:sketch', {page_id: obbSocket.current_page.page_id, stroke: stroke});
        });
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

};

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
*/
