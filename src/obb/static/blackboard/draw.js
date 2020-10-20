$(document).ready(function () {
    let token = $('meta[name=session-token]').attr("content");

    let sketchpad_global_canvas = $('#contentSketchpadGlobal')
    $.sketchpadGlobal = new Atrament(document.querySelector('#contentSketchpadGlobal'));
    $.sketchpadGlobal.recordStrokes = true;

    $.sketchpadGlobal.width = sketchpad_global_canvas.attr('width')
    $.sketchpadGlobal.height = sketchpad_global_canvas.attr('height')

    $(document).on('content:change', function () {
        let sketchpad_canvas = $('#contentSketchpadGlobal')

        $.sketchpadGlobal.width = sketchpad_canvas.attr('width')
        $.sketchpadGlobal.height = sketchpad_canvas.attr('height')
    });

    $.sketchpadGlobal.addEventListener('strokerecorded', ({stroke}) => {
        for (var i = 0; i < stroke.points.length; i++) {
            stroke.points[i].x /= $.sketchpadGlobal.width
            stroke.points[i].y /= $.sketchpadGlobal.height
        }
        $.socket.emit('room:update:draw', {token: token, stroke: stroke});
    });

    let sketchpad_user_canvas = $('#contentSketchpadUser')
    $.sketchpad_user_canvas = new Atrament(document.querySelector('#contentSketchpadUser'));
    $.sketchpad_user_canvas.recordStrokes = true;

    $.sketchpad_user_canvas.width = sketchpad_user_canvas.attr('width')
    $.sketchpad_user_canvas.height = sketchpad_user_canvas.attr('height')

    $(document).on('content:change', function () {
        let sketchpad_canvas = $('#contentSketchpadUser')

        $.sketchpad_user_canvas.width = sketchpad_canvas.attr('width')
        $.sketchpad_user_canvas.height = sketchpad_canvas.attr('height')
    });

})

$(document).on('socket:ready', function () {

    $.socket.on('room:joined', function (msg) {
        let user = msg.user
        if (user.allow_draw) {
            $('#contentSketchpadUser').css('z-index', 1)
        } else {
            $('#contentSketchpadUser').css('z-index', 4)
        }
    });

    $.socket.on('room:updated:user', function (msg) {
        let user = msg.user
        if (user.allow_draw) {
            $('#contentSketchpadUser').css('z-index', 1)
        } else {
            $('#contentSketchpadUser').css('z-index', 4)
        }
    });

    $.socket.on('room:draw:stroke', function (msg) {
        if (msg.creator.user_id === $.user.user_id)
            return

        $.sketchpadGlobal.recordStrokes = false;

        let stroke = msg.stroke
        // set drawing options
        $.sketchpadGlobal.mode = stroke.mode;
        $.sketchpadGlobal.weight = stroke.weight;
        $.sketchpadGlobal.smoothing = stroke.smoothing;
        $.sketchpadGlobal.color = stroke.color;
        $.sketchpadGlobal.adaptiveStroke = stroke.adaptiveStroke;

        // don't want to modify original data
        const points = stroke.points.slice();

        let firstPoint = points.shift();
        firstPoint.x *= $.sketchpadGlobal.width;
        firstPoint.y *= $.sketchpadGlobal.height;
        // beginStroke moves the "pen" to the given position and starts the path
        $.sketchpadGlobal.beginStroke(firstPoint.x, firstPoint.y);

        let prevPoint = firstPoint;
        while (points.length > 0) {
            let point = points.shift();
            point.x *= $.sketchpadGlobal.width;
            point.y *= $.sketchpadGlobal.height;

            // the `draw` method accepts the current real coordinates
            // (i. e. actual cursor position), and the previous processed (filtered)
            // position. It returns an object with the current processed position.
            const {x, y} = $.sketchpadGlobal.draw(point.x, point.y, prevPoint.x, prevPoint.y);

            // the processed position is the one where the line is actually drawn to
            // so we have to store it and pass it to `draw` in the next step
            prevPoint = {x, y};
        }

        // endStroke closes the path
        $.sketchpadGlobal.endStroke(prevPoint.x, prevPoint.y);

        $.sketchpadGlobal.recordStrokes = true;
    });
});