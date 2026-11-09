import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

AppDialog {
    id: dialog
    title: "Carica modello"
    height: Math.min(560, (Overlay.overlay ? Overlay.overlay.height : 600) - 80)
    standardButtons: Dialog.Close
    signal loadRequested(string modelId, string modelName)
    signal deleteRequested(string modelId, string modelName)

    contentItem: ListView {
        clip: true; spacing: 8
        model: manche.view.models
        ScrollBar.vertical: ScrollBar {}
        delegate: Rectangle {
            id: card
            required property var modelData
            width: ListView.view.width - 12
            implicitHeight: body.implicitHeight + 20
            radius: 10; color: Theme.colors.surface; border.color: modelData.current ? Theme.colors.controlAccent : Theme.colors.border
            ColumnLayout {
                id: body
                anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 12 }
                spacing: 4
                RowLayout {
                    Label { text: card.modelData.name; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
                    Pill { text: card.modelData.current ? card.modelData.category + " · in uso" : card.modelData.category }
                    Button { text: "Carica"; highlighted: true; onClicked: dialog.loadRequested(card.modelData.id, card.modelData.name) }
                    ToolButton {
                        visible: card.modelData.custom; text: "⋯"; onClicked: menu.open()
                        Menu { id: menu; MenuItem { text: "Elimina modello…"; onTriggered: dialog.deleteRequested(card.modelData.id, card.modelData.name) } }
                    }
                }
                Label { visible: card.modelData.description !== ""; text: card.modelData.description; opacity: 0.8; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                Label { text: card.modelData.preview; font.pixelSize: 12; opacity: 0.65; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
        }
    }
}
