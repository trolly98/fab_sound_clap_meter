import QtQuick

ScoreStyleBase {
    id: root
    Rectangle { anchors.fill: parent; color: root.colors.background }

    Canvas {
        id: canvas
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height * 1.6) * 0.9
        height: width * 0.62
        onPaint: {
            var ctx = getContext("2d"); ctx.reset()
            var cx = width / 2, cy = height * 0.92, r = width * 0.42
            ctx.lineWidth = r * 0.16; ctx.lineCap = "round"
            ctx.strokeStyle = root.colors.track
            ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI); ctx.stroke()
            ctx.strokeStyle = root.colors.scaleColor(root.progress)
            ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, Math.PI + Math.PI * root.progress); ctx.stroke()
        }
        Connections {
            target: root
            function onProgressChanged() { canvas.requestPaint() }
            function onColorsChanged() { canvas.requestPaint() }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.5
        text: root.scoreText; color: root.colors.textPrimary; font.pixelSize: parent.height * 0.28; font.bold: true
    }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.84
        text: "APPLAUSE " + (root.applauseRunning ? root.applauseScore : root.applauseFinalScore).toFixed(1)
        color: root.colors.accent; font.pixelSize: parent.height * 0.07; font.bold: true
    }
}
