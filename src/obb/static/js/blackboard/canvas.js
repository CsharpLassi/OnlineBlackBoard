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
            obbContentSketchCanvas.loadSketch(msg.user.currentPage);
        });

        obbSocket.on('self:update', function (msg) {
            // Todo: ChangeList
            obbContentSketchCanvas.loadSketch(msg.user.currentPage);
        });

        obbSocket.on('room:get:sketch', function (msg) {
            obbContentSketchCanvas.clearPage(msg.pageId);
            msg.strokes.forEach(stroke => {
                obbContentSketchCanvas.updateSketch(msg.mode, stroke, msg.pageId);
            });
        });

        obbSocket.on('room:clear:sketch', function (msg) {
            obbContentSketchCanvas.clearPage(msg.pageId);
        });

        obbSocket.on('room:add:sketch', function (msg) {
            if (msg.creatorId !== obbSocket.user.sessionId)
                obbContentSketchCanvas.updateSketch(msg.mode, msg.stroke, msg.pageId);
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
        obbContentSketchCanvas.clear();

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
    updateSketch: function (mode, stroke, pageId = null) {
        obbContentBox.config.item.filter(function () {
                let divPageId = $(this).data("pageid")
                return (divPageId === 'current' && (!pageId || pageId === obbSocket.user.currentPage)) || divPageId === pageId;
            }
        ).each(function () {
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
    clearPage: function (pageId = null) {
        obbContentBox.config.item.filter(function () {
                let divPageId = $(this).data("pageid")
                return (divPageId === 'current' && (!pageId || pageId === obbSocket.user.currentPage)) || divPageId === pageId;
            }
        ).each(function () {
            $(this).children('.contentSketchpad').each(function () {
                let atrament = $(this).data('atrament')

                atrament.clear();

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
            let points = []

            let last_point = {}

            for (let i = 0; i < stroke.points.length; i++) {
                let x = stroke.points[i].x / atrament.width ;
                let y = stroke.points[i].y / atrament.height;
                //let x = Math.round( x/ atrament.width * 100) / 100;
                //let y = Math.round(y/ atrament.height * 100) / 100;

                if (last_point && last_point.x === x && last_point.y === y)
                    continue

                last_point['x'] = x;
                last_point['y'] = y;

                points.push({
                    x: x,
                    y: y,
                });
            }

            stroke.points = points

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
