import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Item {
    id: root
    readonly property var v: manche.view
    readonly property var run: v.run
    signal openConfig()

    ColumnLayout {
        visible: !root.run.hasRound
        anchors.centerIn: parent; spacing: 12
        Label { text: "Nessuna manche configurata"; font.pixelSize: 22; font.bold: true; Layout.alignment: Qt.AlignHCenter }
        Label { text: "Aggiungi almeno una manche nella configurazione per iniziare."; opacity: 0.7; Layout.alignment: Qt.AlignHCenter }
        Button { text: "Apri la configurazione"; highlighted: true; Layout.alignment: Qt.AlignHCenter; onClicked: root.openConfig() }
    }

    Loader {
        anchors.fill: parent
        active: root.run.hasRound
        sourceComponent: RowLayout {
            spacing: 16

            Rectangle {
                Layout.horizontalStretchFactor: 30; Layout.preferredWidth: 0; Layout.fillWidth: true; Layout.fillHeight: true
                Layout.maximumWidth: 380
                radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border
                ColumnLayout {
                    anchors { fill: parent; margins: 12 }
                    RowLayout {
                        Label { text: "Ordine delle manche"; font.bold: true; Layout.fillWidth: true }
                        Pill { text: root.v.header.active + " attive" }
                    }
                    Flickable {
                        Layout.fillWidth: true; Layout.fillHeight: true
                        clip: true; contentWidth: width; contentHeight: navColumn.implicitHeight
                        ScrollBar.vertical: ScrollBar {}
                        Column {
                            id: navColumn
                            width: parent.width - 10; spacing: 4
                            Repeater {
                                model: root.run.entries
                                RoundNavItem {
                                    required property var modelData
                                    width: navColumn.width
                                    entry: modelData
                                    navEnabled: !root.v.live
                                    onClicked: manche.selectRound(modelData.id)
                                }
                            }
                        }
                    }
                }
            }

            Flickable {
                id: stage
                Layout.horizontalStretchFactor: 70; Layout.preferredWidth: 0; Layout.fillWidth: true; Layout.fillHeight: true
                clip: true; contentWidth: width; contentHeight: stageColumn.implicitHeight + 8
                ScrollBar.vertical: ScrollBar {}
                ColumnLayout {
                    id: stageColumn
                    width: stage.width - 14; spacing: 14

                    RowLayout {
                        ColumnLayout {
                            spacing: 0
                            Label { text: root.run.round.eyebrow; font.pixelSize: 12; opacity: 0.7 }
                            Label { text: root.run.round.name; font.pixelSize: 26; font.bold: true }
                        }
                        Item { Layout.fillWidth: true }
                        Pill { text: root.run.round.label }
                    }
                    Label { visible: root.run.round.notes !== ""; text: root.run.round.notes; wrapMode: Text.WordWrap; opacity: 0.75; Layout.fillWidth: true }

                    Flow {
                        Layout.fillWidth: true; spacing: 10
                        Repeater {
                            model: root.run.slots
                            SlotButton {
                                required property var modelData
                                slot: modelData
                                navEnabled: !root.v.live
                                onClicked: manche.selectSlot(modelData.key)
                            }
                        }
                    }

                    MeasureConsole { Layout.fillWidth: true; slot: root.run.slot }

                    VoteCards {
                        Layout.fillWidth: true
                        cards: root.run.cards
                        canExclude: !root.v.locked
                        onExcludeRequested: function(sessionId) { excludeDialog.pending = sessionId; excludeDialog.open() }
                    }

                    RowLayout {
                        Button { text: "Storico misure"; flat: true; enabled: root.run.hasHistory; onClicked: historyDialog.open() }
                        Item { Layout.fillWidth: true }
                        Button { text: "Vai al prossimo turno →"; highlighted: true; enabled: root.run.canNext; onClicked: manche.nextTurn() }
                    }
                }
            }
        }
    }

    HistoryDialog { id: historyDialog }
    ConfirmDialog {
        id: excludeDialog
        property string pending: ""
        title: "Escludere la misura straordinaria?"
        body: "Il valore verrà tolto dalla media della manche. Resta visibile nello storico."
        confirmText: "Escludi"
        onConfirmed: manche.excludeExtra(pending)
    }
}
