import QtQuick

ScoreStyleBase {
    Rectangle { anchors.fill: parent; color: "#0b0b12" }

    Row {
        anchors.centerIn: parent
        spacing: parent.width * 0.06

        Column {
            spacing: 6
            Repeater {
                model: 10
                Rectangle {
                    required property int index
                    readonly property int level: 10 - index
                    width: 260; height: (parent.parent.parent.height * 0.82) / 10 - 6
                    radius: 6
                    color: Qt.hsla(0.33 - 0.33 * (level - 1) / 9, 0.9, 0.5, 1)
                    opacity: score >= level ? 1.0 : 0.12
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                    Text {
                        anchors.centerIn: parent; text: parent.level
                        color: "white"; font.pixelSize: parent.height * 0.5; font.bold: true
                    }
                }
            }
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: scoreText
            color: "white"; font.pixelSize: 220; font.bold: true
        }
    }
}
