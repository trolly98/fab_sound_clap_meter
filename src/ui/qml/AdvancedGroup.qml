import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Gruppo a scomparsa (chiuso all'avvio): clic sul titolo per aprire o chiudere.
ColumnLayout {
    id: root
    property string title: "Advanced settings"
    property bool expanded: false
    default property alias content: body.data
    Layout.fillWidth: true

    Item {
        Layout.fillWidth: true
        implicitHeight: header.implicitHeight + 12
        Label {
            id: header
            anchors.verticalCenter: parent.verticalCenter
            text: (root.expanded ? "▾  " : "▸  ") + root.title
            font.bold: true
        }
        TapHandler { onTapped: root.expanded = !root.expanded }
    }
    ColumnLayout { id: body; visible: root.expanded; Layout.fillWidth: true; Layout.leftMargin: 8; spacing: 8 }
}
