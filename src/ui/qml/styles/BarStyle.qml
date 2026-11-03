import QtQuick

ScoreStyleBase {
    id: root
    Rectangle { anchors.fill: parent; color: root.colors.background }

    Row {
        anchors.centerIn: parent
        spacing: root.width * 0.06

        Column {
            spacing: 6
            Repeater {
                model: 10
                Rectangle {
                    required property int index
                    readonly property int level: 10 - index
                    width: 260; height: (root.height * 0.82) / 10 - 6
                    radius: 6
                    readonly property bool lit: root.actualScore >= level
                    color: lit || !root.colors.inactiveUsesTrack ? root.colors.scaleColor((level - 1) / 9) : root.colors.track
                    opacity: lit ? 1.0 : root.colors.inactiveOpacity
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                    Text {
                        anchors.centerIn: parent; text: parent.level
                        color: root.colors.contrastText(parent.color)
                        font.pixelSize: parent.height * 0.5; font.bold: true
                    }
                }
            }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10
            Text { text: root.scoreText; color: root.colors.textPrimary; font.pixelSize: 220; font.bold: true }
            Text {
                text: "APPLAUSE " + (root.applauseRunning ? root.applauseScore : root.applauseFinalScore).toFixed(1)
                color: root.colors.accent; font.pixelSize: 56; font.bold: true
            }
        }
    }
}
