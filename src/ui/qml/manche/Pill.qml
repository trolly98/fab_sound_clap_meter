import QtQuick
import QtQuick.Controls
import ".."

// Etichetta tondeggiante: tone "" | "good" | "warn"
Rectangle {
    id: root
    property string text: ""
    property string tone: ""
    readonly property color toneColor: tone === "good" ? Theme.colors.good : tone === "warn" ? Theme.colors.warn : Theme.colors.border
    implicitWidth: label.implicitWidth + 18
    implicitHeight: label.implicitHeight + 6
    radius: height / 2
    color: "transparent"
    border.width: 1
    border.color: toneColor
    Label {
        id: label
        anchors.centerIn: parent
        text: root.text
        font.pixelSize: 12
        color: root.tone === "" ? Theme.colors.textPrimary : root.toneColor
    }
}
