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
            ctx.lineWidth = r * 0.16; ctx.lineCap = "round"
            ctx.strokeStyle = "#262633"
            ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI); ctx.stroke()
            ctx.strokeStyle = Qt.hsla(0.33 - 0.33 * root.progress, 0.9, 0.5, 1)
            ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, Math.PI + Math.PI * root.progress); ctx.stroke()
        }
        Connections { target: root; function onProgressChanged() { canvas.requestPaint() } }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.5
        text: root.scoreText; color: "white"; font.pixelSize: parent.height * 0.28; font.bold: true
    }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.84
        text: "APPLAUSE " + (root.applauseRunning ? root.applauseScore : root.applauseFinalScore).toFixed(1)
        color: "#ffd54f"; font.pixelSize: parent.height * 0.07; font.bold: true
    }
}
