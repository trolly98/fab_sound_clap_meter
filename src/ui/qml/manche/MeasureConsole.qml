import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

// Console della misura: avvio manuale, sessione automatica (start e stop da soli), correzioni.
Rectangle {
    id: root
    property var slot
    readonly property bool live: manche.view.live
    readonly property var applause: clapMeter.applause
    implicitHeight: column.implicitHeight + 24
    radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border

    component Readout: ColumnLayout {
        property string caption: ""
        property string value: ""
        spacing: 0
        Label { text: parent.caption; font.pixelSize: 12; opacity: 0.7 }
        Label { text: parent.value; font.pixelSize: 28; font.bold: true }
    }

    ColumnLayout {
        id: column
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 12 }
        spacing: 10

        RowLayout {
            Label { text: "Console applausometro · " + root.slot.label + " " + root.slot.personName; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
            Pill { text: root.slot.outcome; tone: root.slot.outcomeTone }
        }
        RowLayout {
            spacing: 32
            Readout { caption: "Voto live"; value: clapMeter.applause_score.toFixed(1) }
            Readout { caption: "Voto definitivo"; value: root.slot.voteText }
            Readout {
                caption: !root.live ? "Tempo" : root.applause.timed ? "Rimanenti" : "Trascorsi"
                value: !root.live ? "—" : (root.applause.timed ? root.applause.remainingS : root.applause.elapsedS).toFixed(1) + " s"
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 10; radius: 5; color: Theme.colors.meterTrack
            Rectangle {
                width: parent.width * Math.min(1, clapMeter.applause_score / 10); height: parent.height; radius: 5
                color: Theme.colors.meterFill
            }
        }
        Label {
            Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.75; font.pixelSize: 12
            text: root.live ? (root.applause.timed ? "Sessione automatica · si ferma da sola tra " + root.applause.remainingS.toFixed(1) + " s"
                                                   : "Misura in corso · premi Stop quando l’applauso finisce")
                            : "Arresto manuale oppure sessione automatica da " + Math.round(root.applause.sessionDurationS) + " s · scala da 1 a 10"
        }

        Flow {
            Layout.fillWidth: true; spacing: 8
            Button { visible: root.live; text: "■ Stop"; highlighted: true; onClicked: manche.stopMeasurement() }
            Button { visible: root.live; text: "Annulla misura"; flat: true; onClicked: manche.cancelMeasurement() }

            Button { visible: !root.live && root.slot.canStart; text: "▶ Avvia misura"; highlighted: true
                     onClicked: manche.startMeasurement("new", false) }
            Button { visible: !root.live && root.slot.canStart; text: "⏱ Sessione automatica"
                     onClicked: manche.startMeasurement("new", true) }
            Button { visible: !root.live && root.slot.canCorrect; text: "Sostituisci voto…"; onClicked: replaceDialog.open() }
            Button { visible: !root.live && root.slot.canCorrect; text: "Misura straordinaria…"; onClicked: extraDialog.open() }

            Row {
                visible: !root.live && (root.slot.canStart || root.slot.canCorrect)
                spacing: 8
                Label { text: "Durata sessione"; anchors.verticalCenter: parent.verticalCenter }
                SpinBox {
                    from: Math.round(root.applause.sessionMinS); to: Math.round(root.applause.sessionMaxS); stepSize: 1
                    value: Math.round(root.applause.sessionDurationS); editable: true
                    onValueModified: root.applause.setSessionDurationS(value)
                    textFromValue: function(v) { return v + " s" }
                    valueFromText: function(t) { return parseInt(t) }
                }
            }
        }
    }

    MeasureDialog {
        id: replaceDialog
        mode: "replace"
        title: "Sostituire il voto " + root.slot.label + "?"
        body: "Il voto attuale (" + root.slot.voteText + ") verrà sostituito dal risultato di una nuova misura. La misura precedente resta nello storico."
    }
    MeasureDialog {
        id: extraDialog
        mode: "extra"
        title: "Misura straordinaria " + root.slot.label
        body: "Il risultato si aggiunge ai voti ordinari e entra nella media della manche. Il voto già registrato non cambia. Potrai escluderla dalla media con la ×."
    }
}
