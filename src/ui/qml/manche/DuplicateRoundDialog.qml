import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

AppDialog {
    id: dialog
    title: "Duplica una manche"
    standardButtons: Dialog.Close
    contentItem: ColumnLayout {
        spacing: 6
        Label { text: "Scegli la manche da copiare. La copia nasce senza voti."; opacity: 0.75; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Repeater {
            model: manche.view.config.rounds
            Button {
                required property var modelData
                Layout.fillWidth: true; text: modelData.name
                onClicked: { dialog.close(); manche.duplicateRound(modelData.id) }
            }
        }
    }
}
