import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    property var entry
    property bool navEnabled: true
    signal clicked()
    Layout.fillWidth: true
    implicitHeight: 56; radius: 8
    color: entry.selected ? Qt.alpha(Theme.colors.controlAccent, 0.18) : "transparent"
    border.color: entry.selected ? Theme.colors.controlAccent : "transparent"
    opacity: entry.active ? 1 : 0.55
    RowLayout {
        anchors { fill: parent; margins: 8 }
        spacing: 10
        Label { text: root.entry.number; opacity: 0.6 }
        ColumnLayout {
            Layout.fillWidth: true; spacing: 0
            Label { text: root.entry.name; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
            Label { text: root.entry.label; font.pixelSize: 12; opacity: 0.7; elide: Text.ElideRight; Layout.fillWidth: true }
        }
        Pill { text: root.entry.recorded + "/" + root.entry.count; tone: root.entry.recorded === root.entry.count ? "good" : "" }
    }
    TapHandler { enabled: root.navEnabled; onTapped: root.clicked() }
}
