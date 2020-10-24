$(document).on('socket:ready', function () {


    $.socket.on('room:draw:stroke', function (msg) {
        if (msg.creator !== null && msg.creator.user_id === $.user.user_id)
            return
        let old_record = $.sketchpadGlobal.recordStrokes
        let old_mode = $.sketchpadGlobal.mode
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

        $.sketchpadGlobal.recordStrokes = old_record;
        $.sketchpadGlobal.mode = old_mode;
    });
});