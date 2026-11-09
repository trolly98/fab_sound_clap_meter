import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    readonly property var header: manche.view.header
    implicitHeight: content.implicitHeight + 24
    radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border

    RowLayout {
        id: content
        anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 14 }
        spacing: 22

        ColumnLayout {
            spacing: 0
            Label { text: root.header.modelName; font.pixelSize: 12; opacity: 0.7 }
            Label { text: "Manche"; font.pixelSize: 24; font.bold: true }
        }
        Repeater {
            model: ["A", "B"]
            RowLayout {
                required property string modelData
                spacing: 8
                PersonBadge { person: modelData }
                ColumnLayout {
                    spacing: 0
                    Label { text: root.header.names[modelData]; font.bold: true; elide: Text.ElideRight; Layout.maximumWidth: 160 }
                    Label { text: root.header.totalsLabel; font.pixelSize: 11; opacity: 0.7 }
                }
                Label { text: root.header.totals[modelData]; font.pixelSize: 26; font.bold: true }
            }
        }
        Item { Layout.fillWidth: true }
        ColumnLayout {
            spacing: 4
            Label { text: root.header.status; font.bold: true; Layout.alignment: Qt.AlignRight }
            RowLayout {
                Rectangle {
                    implicitWidth: 140; implicitHeight: 8; radius: 4; color: Theme.colors.meterTrack
                    Rectangle { width: parent.width * root.header.progress / 100; height: parent.height; radius: 4; color: Theme.colors.good }
                }
                Label { text: root.header.done + " / " + root.header.active + " manche"; font.pixelSize: 12; opacity: 0.75 }
            }
        }
        Button { text: "Nuova gara…"; flat: true; enabled: !manche.view.live; onClicked: newGameDialog.open() }
    }

    AppDialog {
        id: newGameDialog
        title: "Nuova gara"
        contentItem: ColumnLayout {
            spacing: 10
            Label { Layout.fillWidth: true; wrapMode: Text.WordWrap
                    text: "Voti, storico e proclamazione vengono azzerati. I nomi dei concorrenti restano." }
            Button { Layout.fillWidth: true; text: "Stesse manche di adesso"; onClicked: { newGameDialog.close(); manche.newGame("current") } }
            Button { Layout.fillWidth: true; text: "Gara di Bugie (modello predefinito)"; onClicked: { newGameDialog.close(); manche.newGame("builtin") } }
            Button { Layout.fillWidth: true; text: "Da zero (nessuna manche)"; onClicked: { newGameDialog.close(); manche.newGame("empty") } }
            Button { Layout.fillWidth: true; text: "Annulla"; flat: true; onClicked: newGameDialog.close() }
        }
    }
}
