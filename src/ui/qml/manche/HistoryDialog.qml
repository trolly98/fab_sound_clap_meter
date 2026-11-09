import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

AppDialog {
    id: dialog
    title: "Storico misure"
    height: Math.min(520, (Overlay.overlay ? Overlay.overlay.height : 600) - 80)
    standardButtons: Dialog.Close
    contentItem: ColumnLayout {
        Label { text: "Ogni riga è una sessione di ascolto di questa gara."; opacity: 0.7; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        ListView {
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true; spacing: 6
            model: manche.view.history
            ScrollBar.vertical: ScrollBar {}
            delegate: Rectangle {
                required property var modelData
                width: ListView.view.width - 12
                implicitHeight: row.implicitHeight + 16
                radius: 8; color: Theme.colors.surface; border.color: Theme.colors.border
                ColumnLayout {
                    id: row
                    anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 10 }
                    spacing: 2
                    RowLayout {
                        Label { text: modelData.round; font.bold: true }
                        Label { text: modelData.turn + " · " + modelData.person; opacity: 0.7 }
                        Item { Layout.fillWidth: true }
                        Pill { text: modelData.status; tone: modelData.status === "Valida" ? "good" : "warn" }
                    }
                    Label {
                        text: modelData.mode + " · voto " + modelData.value + " · " + modelData.time
                              + (modelData.included ? " · nella media" : "") + (modelData.reason ? " · " + modelData.reason : "")
                        font.pixelSize: 12; opacity: 0.7
                    }
                }
            }
        }
    }
}
