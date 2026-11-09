import QtQuick
import QtQuick.Controls

// Cambio del numero di voti: se la sequenza e' personalizzata si sceglie come adattarla; se escono voti si conferma.
AppDialog {
    id: dialog
    property string roundId: ""
    property int count: 1
    property int removed: 0
    property bool needsChoice: false
    title: "Cambiare il numero di voti?"
    function apply(mode) { dialog.close(); manche.setRoundCount(roundId, count, mode) }
    contentItem: Item {
        implicitHeight: message.implicitHeight
        Label {
            id: message
            width: parent.width; wrapMode: Text.WordWrap
            text: (dialog.needsChoice ? "La sequenza di questa manche è personalizzata. Come vuoi adattarla a " + dialog.count + " voti per sfidante?\n\n" : "")
                  + (dialog.removed > 0 ? "Attenzione: " + dialog.removed + " voti già registrati verranno eliminati dal tabellone." : "")
        }
    }
    footer: DialogButtons {
        Button { visible: dialog.needsChoice; text: "Conserva l’ordine"; highlighted: true; onClicked: dialog.apply("adapt") }
        Button { visible: dialog.needsChoice; text: "Rigenera alternata"; onClicked: dialog.apply("regenerate") }
        Button { visible: !dialog.needsChoice; text: "Elimina e procedi"; highlighted: true; onClicked: dialog.apply("adapt") }
        Button { text: "Annulla"; onClicked: dialog.close() }
    }
}
