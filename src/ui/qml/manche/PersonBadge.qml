import QtQuick
import QtQuick.Controls
import ".."

Rectangle {
    id: root
    property string person: "A"
    readonly property color fill: person === "A" ? Theme.colors.personA : Theme.colors.personB
    implicitWidth: 28; implicitHeight: 28; radius: 14
    color: fill
    Label {
        anchors.centerIn: parent
        text: root.person; font.bold: true
        color: Theme.colors.contrastText(root.fill)
    }
}
