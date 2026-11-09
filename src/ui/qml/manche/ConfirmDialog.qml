import QtQuick
import QtQuick.Controls

AppDialog {
    id: dialog
    property string body: ""
    property string confirmText: "Conferma"
    signal confirmed()
    contentItem: Item {
        implicitHeight: message.implicitHeight
        Label { id: message; width: parent.width; text: dialog.body; wrapMode: Text.WordWrap }
    }
    footer: DialogButtons {
        Button { text: dialog.confirmText; highlighted: true; onClicked: { dialog.close(); dialog.confirmed() } }
        Button { text: "Annulla"; onClicked: dialog.close() }
    }
}
