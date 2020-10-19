$(document).ready(function () {
    const canvas = document.querySelector('#contentSketchpad');
    $.sketchpad = new Atrament(canvas);
    $.sketchpad.recordStrokes = true;


    let sketchpad_canvas = $('#contentSketchpad')

    $.sketchpad.width = sketchpad_canvas.attr('width')
    $.sketchpad.height = sketchpad_canvas.attr('height')

    $(document).on('content:change', function () {
        let sketchpad_canvas = $('#contentSketchpad')

        $.sketchpad.width = sketchpad_canvas.attr('width')
        $.sketchpad.height = sketchpad_canvas.attr('height')
    });

    $.sketchpad.addEventListener('strokerecorded', ({stroke}) => {
        let room_id = $.urlParam('room_id');
        for (var i = 0; i < stroke.points.length; i++) {
            stroke.points[i].x /= $.sketchpad.width
            stroke.points[i].y /= $.sketchpad.height
        }
        $.socket.emit('room:update:draw', {room_id: room_id, stroke: stroke});
    });


})

$(document).on('socket:ready', function () {
    $.socket.on('room:draw:stroke', function (msg) {
        if (msg.creator.user_id === $.user.user_id)
            return

        $.sketchpad.recordStrokes = false;

        let stroke = msg.stroke
        // set drawing options
        $.sketchpad.mode = stroke.mode;
        $.sketchpad.weight = stroke.weight;
        $.sketchpad.smoothing = stroke.smoothing;
        $.sketchpad.color = stroke.color;
        $.sketchpad.adaptiveStroke = stroke.adaptiveStroke;

        // don't want to modify original data
        const points = stroke.points.slice();

        let firstPoint = points.shift();
        firstPoint.x *= $.sketchpad.width;
        firstPoint.y *= $.sketchpad.height;
        // beginStroke moves the "pen" to the given position and starts the path
        $.sketchpad.beginStroke(firstPoint.x, firstPoint.y);

        let prevPoint = firstPoint;
        while (points.length > 0) {
            let point = points.shift();
            point.x *= $.sketchpad.width;
            point.y *= $.sketchpad.height;

            // the `draw` method accepts the current real coordinates
            // (i. e. actual cursor position), and the previous processed (filtered)
            // position. It returns an object with the current processed position.
            const {x, y} = $.sketchpad.draw(point.x, point.y, prevPoint.x, prevPoint.y);

            // the processed position is the one where the line is actually drawn to
            // so we have to store it and pass it to `draw` in the next step
            prevPoint = {x, y};
        }

        // endStroke closes the path
        $.sketchpad.endStroke(prevPoint.x, prevPoint.y);

        $.sketchpad.recordStrokes = true;
    });
});