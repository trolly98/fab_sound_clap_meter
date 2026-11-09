import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

// Riga dell'elenco manche: trascina l'icona ⠿ per spostarla, oppure usa le frecce. Il menu ⋯ ha duplica ed elimina.
Rectangle {
    id: root
    property var item
    property int rowIndex: 0
    property int rowCount: 1
    property real rowPitch: 50          // altezza di una riga + spazio tra le righe
    property bool editable: true
    property Flickable scroller: null      // pannello scorrevole da fermare mentre si trascina
    property real dragOffset: 0
    signal selectRequested()
    signal activeToggled(bool on)
    signal moveRequested(int target)
    signal duplicateRequested()
    signal deleteRequested()

    function finishDrag(dy) {
        var target = Math.floor((rowIndex * rowPitch + height / 2 + dy) / rowPitch)
        target = Math.max(0, Math.min(rowCount - 1, target))
        if (target !== rowIndex) moveRequested(target)
    }

    implicitHeight: 46; radius: 8
    color: item.selected ? Qt.alpha(Theme.colors.controlAccent, 0.18) : "transparent"
    border.color: item.selected ? Theme.colors.controlAccent : Theme.colors.border
    opacity: item.active ? 1 : 0.6
    z: dragOffset !== 0 ? 10 : 0
    transform: Translate { y: root.dragOffset }

    RowLayout {
        anchors { fill: parent; leftMargin: 8; rightMargin: 4 }
        spacing: 4
        Item {
            implicitWidth: 30; implicitHeight: root.implicitHeight          // area di presa piu' grande del simbolo
            Label { anchors.centerIn: parent; text: "⠿"; font.pixelSize: 22; opacity: root.editable ? 0.7 : 0.3 }
            TapHandler { onPressedChanged: if (root.scroller) root.scroller.interactive = !pressed }
            DragHandler {
                id: drag
                property real lastDy: 0
                target: null; enabled: root.editable; yAxis.enabled: true; xAxis.enabled: false
                grabPermissions: PointerHandler.CanTakeOverFromAnything
                onTranslationChanged: if (active) { root.dragOffset = translation.y; lastDy = translation.y }
                onActiveChanged: if (!active) { root.dragOffset = 0; root.finishDrag(lastDy); lastDy = 0 }
            }
        }
        CheckBox { checked: root.item.active; enabled: root.editable; onToggled: root.activeToggled(checked) }
        Label {
            Layout.fillWidth: true; elide: Text.ElideRight
            text: root.item.name + (root.item.active ? "" : " · disattivata"); font.bold: root.item.selected
            TapHandler { onTapped: root.selectRequested() }
        }
        ToolButton { text: "↑"; enabled: root.editable && root.item.canUp; onClicked: root.moveRequested(root.rowIndex - 1) }
        ToolButton { text: "↓"; enabled: root.editable && root.item.canDown; onClicked: root.moveRequested(root.rowIndex + 1) }
        ToolButton {
            text: "⋯"; enabled: root.editable; onClicked: menu.open()
            Menu {
                id: menu
                MenuItem { text: "Duplica manche"; onTriggered: root.duplicateRequested() }
                MenuItem { text: "Elimina manche…"; onTriggered: root.deleteRequested() }
            }
        }
    }
}
