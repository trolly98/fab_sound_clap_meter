import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    property var slot
    property bool navEnabled: true
    signal clicked()
    implicitWidth: 168; implicitHeight: 82; radius: 10
    color: slot.selected ? Qt.alpha(Theme.colors.controlAccent, 0.18) : Theme.colors.surface
    border.width: slot.selected ? 2 : 1
    border.color: slot.selected ? Theme.colors.controlAccent : Theme.colors.border
    ColumnLayout {
        anchors { fill: parent; margins: 10 }
        spacing: 2
        RowLayout {
            PersonBadge { person: root.slot.person; implicitWidth: 22; implicitHeight: 22 }
            Label { text: root.slot.label + " · " + root.slot.turn; font.bold: true }
        }
        Label { text: root.slot.personName; font.pixelSize: 12; opacity: 0.7; elide: Text.ElideRight; Layout.fillWidth: true }
        Label {
            text: root.slot.status; font.pixelSize: 13
            color: root.slot.measuring || root.slot.status.charAt(0) === "✓" ? Theme.colors.good
                   : root.slot.status === "Vuota" || root.slot.status === "Annullata" ? Theme.colors.warn : Theme.colors.textPrimary
        }
    }
    TapHandler { enabled: root.navEnabled; onTapped: root.clicked() }
}
