import QtQuick
import QtQuick.Controls

// Conferma di una nuova misura su un turno che ha gia' un voto (sostitutiva o straordinaria).
AppDialog {
    id: dialog
    property string mode: "replace"
    property string body: ""
    function start(auto) { dialog.close(); manche.startMeasurement(dialog.mode, auto) }
    contentItem: Item {
        implicitHeight: message.implicitHeight
        Label { id: message; width: parent.width; text: dialog.body; wrapMode: Text.WordWrap }
    }
    footer: DialogButtons {
        Button { text: "Avvia misura"; highlighted: true; onClicked: dialog.start(false) }
        Button { text: "Sessione automatica (" + Math.round(clapMeter.applause.sessionDurationS) + " s)" ; onClicked: dialog.start(true) }
        Button { text: "Annulla"; onClicked: dialog.close() }
    }
}
