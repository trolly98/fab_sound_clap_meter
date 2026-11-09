import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

// Un turno della sequenza: trascinabile (⠿) o spostabile con ◀ ▶.
Rectangle {
    id: root
    property var turn
    property int tileIndex: 0
    property int tileCount: 1
    property bool editable: true
    property real pitchX: 158
    property real pitchY: 96
    property int perRow: 1
    property Flickable scroller: null      // pannello scorrevole da fermare mentre si trascina
    property real dragX: 0
    property real dragY: 0
    signal moveRequested(int target)

    function finishDrag(dx, dy) {
        var col = Math.floor((x + width / 2 + dx) / pitchX)
        var row = Math.floor((y + height / 2 + dy) / pitchY)
        var target = Math.max(0, Math.min(tileCount - 1, Math.max(0, row) * perRow + Math.max(0, Math.min(perRow - 1, col))))
        if (target !== tileIndex) moveRequested(target)
    }

    width: 150; height: 88; radius: 10
    color: Theme.colors.surface; border.color: Theme.colors.border
    z: (dragX !== 0 || dragY !== 0) ? 10 : 0
    transform: Translate { x: root.dragX; y: root.dragY }

    ColumnLayout {
        anchors { fill: parent; margins: 8 }
        spacing: 2
        RowLayout {
            Item {
                implicitWidth: 26; implicitHeight: 30          // area di presa piu' grande del simbolo
                Label { anchors.centerIn: parent; text: "⠿"; font.pixelSize: 18; opacity: root.editable ? 0.7 : 0.3 }
                TapHandler { onPressedChanged: if (root.scroller) root.scroller.interactive = !pressed }
                DragHandler {
                    property real lastDx: 0
                    property real lastDy: 0
                    target: null; enabled: root.editable
                    grabPermissions: PointerHandler.CanTakeOverFromAnything     // il pannello scorrevole non deve rubare il gesto
                    onTranslationChanged: if (active) { root.dragX = translation.x; root.dragY = translation.y; lastDx = translation.x; lastDy = translation.y }
                    onActiveChanged: if (!active) { root.dragX = 0; root.dragY = 0; root.finishDrag(lastDx, lastDy); lastDx = 0; lastDy = 0 }
                }
            }
            PersonBadge { person: root.turn.person; implicitWidth: 22; implicitHeight: 22 }
            Label { text: root.turn.label; font.bold: true; Layout.fillWidth: true }
            ToolButton { text: "◀"; implicitWidth: 28; implicitHeight: 28; enabled: root.editable && root.tileIndex > 0
                         onClicked: root.moveRequested(root.tileIndex - 1) }
            ToolButton { text: "▶"; implicitWidth: 28; implicitHeight: 28; enabled: root.editable && root.tileIndex < root.tileCount - 1
                         onClicked: root.moveRequested(root.tileIndex + 1) }
        }
        Label { text: root.turn.personName; font.pixelSize: 12; opacity: 0.8; elide: Text.ElideRight; Layout.fillWidth: true }
        Label { text: "Posizione " + root.turn.position; font.pixelSize: 11; opacity: 0.6 }
    }
}
