import QtQuick

ScoreStyleBase {
    id: root
    Rectangle { anchors.fill: parent; color: "#101018" }

    Canvas {
        id: canvas
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height * 1.6) * 0.9
        height: width * 0.62
        onPaint: {
            var ctx = getContext("2d"); ctx.reset()
            var cx = width / 2, cy = height * 0.92, r = width * 0.42
            var start = Math.PI, span = Math.PI
            ctx.lineWidth = r * 0.16; ctx.lineCap = "round"
            ctx.strokeStyle = "#262633"
            ctx.beginPath(); ctx.arc(cx, cy, r, start, start + span); ctx.stroke()
            ctx.strokeStyle = Qt.hsla(0.33 - 0.33 * root.progress, 0.9, 0.5, 1)
            ctx.beginPath(); ctx.arc(cx, cy, r, start, start + span * root.progress); ctx.stroke()
        }
        Connections { target: root; function onProgressChanged() { canvas.requestPaint() } }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.55
        text: scoreText; color: "white"; font.pixelSize: parent.height * 0.3; font.bold: true
    }
}
