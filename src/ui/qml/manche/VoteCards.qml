import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

// Punteggio di manche e voti singoli dei due sfidanti. Le misure straordinarie hanno una × per escluderle dalla media.
RowLayout {
    id: root
    property var cards: []
    property bool canExclude: false
    signal excludeRequested(string sessionId)
    spacing: 12
    Repeater {
        model: root.cards
        Rectangle {
            id: card
            required property var modelData
            Layout.fillWidth: true; Layout.preferredWidth: 0; Layout.horizontalStretchFactor: 1
            implicitHeight: content.implicitHeight + 24
            radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border
            ColumnLayout {
                id: content
                anchors { left: parent.left; right: parent.right; top: parent.top; margins: 12 }
                RowLayout {
                    PersonBadge { person: card.modelData.person }
                    Label { text: card.modelData.name; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                    Label { text: card.modelData.points; font.pixelSize: 26; font.bold: true }
                }
                Flow {
                    Layout.fillWidth: true; spacing: 6
                    Repeater {
                        model: card.modelData.votes
                        Rectangle {
                            id: chip
                            required property var modelData
                            implicitWidth: chipRow.implicitWidth + 16; implicitHeight: 28; radius: 14
                            color: "transparent"; border.color: modelData.extra ? Theme.colors.warn : Theme.colors.border
                            Row {
                                id: chipRow
                                anchors.centerIn: parent; spacing: 6
                                Label { text: chip.modelData.text; anchors.verticalCenter: parent.verticalCenter }
                                Label {
                                    visible: chip.modelData.extra && root.canExclude
                                    text: "×"; color: Theme.colors.danger; font.bold: true
                                    anchors.verticalCenter: parent.verticalCenter
                                    TapHandler { onTapped: root.excludeRequested(chip.modelData.sessionId) }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
