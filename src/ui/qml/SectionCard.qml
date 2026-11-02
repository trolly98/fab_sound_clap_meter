import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Sezione comprimibile: clic sul titolo per aprire/chiudere. Il contenuto va dichiarato dentro.
Rectangle {
    id: root
    property string title: ""
    property bool expanded: true
    default property alias content: body.data

    implicitHeight: column.implicitHeight + 24
    radius: 10
    color: "#262633"
    border.color: "#3a3a52"

    ColumnLayout {
        id: column
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 12 }
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Label { text: root.title; font.pixelSize: 18; font.bold: true; Layout.fillWidth: true }
            Label { text: root.expanded ? "▾" : "▸"; font.pixelSize: 18 }
            TapHandler { onTapped: root.expanded = !root.expanded }
        }
        ColumnLayout { id: body; visible: root.expanded; Layout.fillWidth: true; spacing: 8 }
    }
}
