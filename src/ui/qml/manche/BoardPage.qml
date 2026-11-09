import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Item {
    id: root
    readonly property var board: manche.view.board
    readonly property var names: board.names

    function act(id) {
        if (id === "announce") manche.announce()
        else if (id === "tie") manche.startTie()
        else if (id === "goto-tie") manche.gotoTie()
        else if (id === "reopen") reopenDialog.open()
    }

    component Cell: Label {
        property real share: 1
        Layout.fillWidth: true; Layout.preferredWidth: 0; Layout.horizontalStretchFactor: Math.round(share * 10)
        elide: Text.ElideRight
    }
    component TableRow: RowLayout {
        property var cells: []              // 7 testi
        property bool strong: false
        property bool head: false
        Layout.fillWidth: true; spacing: 8
        Repeater {
            model: parent.cells
            Cell {
                required property var modelData
                required property int index
                share: [3.2, 2.2, 1.2, 1.4, 2.2, 1.2, 1.4][index]
                text: modelData
                font.bold: parent.strong || parent.head
                font.pixelSize: parent.head ? 12 : 14
                opacity: parent.head ? 0.8 : 1
                color: parent.head && (index >= 1 && index <= 3) ? Theme.colors.personA
                       : parent.head && index >= 4 ? Theme.colors.personB : Theme.colors.textPrimary
            }
        }
    }

    Flickable {
        id: flick
        anchors.fill: parent
        clip: true; contentWidth: width; contentHeight: column.implicitHeight + 8
        ScrollBar.vertical: ScrollBar {}
        ColumnLayout {
            id: column
            width: flick.width - 14; spacing: 14

            Rectangle {
                Layout.fillWidth: true; implicitHeight: resultRow.implicitHeight + 28
                radius: 10; color: Theme.colors.surface
                border.width: manche.view.hasResult ? 2 : 1
                border.color: manche.view.hasResult ? Theme.colors.good : Theme.colors.border
                RowLayout {
                    id: resultRow
                    anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 14 }
                    spacing: 16
                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 2
                        Label { text: "Esito della gara"; font.pixelSize: 12; opacity: 0.7 }
                        Label { text: root.board.result.title; font.pixelSize: 24; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        Label { text: root.board.result.body; opacity: 0.75; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    }
                    Flow {
                        Layout.maximumWidth: 360; spacing: 8
                        Repeater {
                            model: root.board.result.actions
                            Button {
                                required property var modelData
                                text: modelData.label; highlighted: modelData.primary; enabled: modelData.enabled
                                onClicked: root.act(modelData.id)
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true; implicitHeight: table.implicitHeight + 28
                radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border
                ColumnLayout {
                    id: table
                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 14 }
                    spacing: 8
                    TableRow { head: true; cells: ["Manche", root.names.A + " · voti", "Manche", "Progressivo", root.names.B + " · voti", "Manche", "Progressivo"] }
                    Repeater {
                        model: root.board.rows
                        TableRow {
                            required property var modelData
                            opacity: modelData.active ? 1 : 0.5
                            cells: [modelData.name + (modelData.active ? "" : " (disattivata)"),
                                    modelData.A.votes, modelData.A.points, modelData.A.total,
                                    modelData.B.votes, modelData.B.points, modelData.B.total]
                        }
                    }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.colors.border }
                    TableRow {
                        strong: true
                        cells: [root.board.totalLabel, "", "", root.board.totals.A, "", "", root.board.totals.B]
                    }
                }
            }

            Repeater {
                model: root.board.ties
                ColumnLayout {
                    required property var modelData
                    Layout.fillWidth: true; spacing: 8
                    Label { text: modelData.name + " · separato dai totali di gara"; font.bold: true }
                    VoteCards { Layout.fillWidth: true; cards: modelData.cards }
                }
            }

            RowLayout {
                Button { text: "Storico misure"; flat: true; enabled: root.board.hasHistory; onClicked: historyDialog.open() }
                Item { Layout.fillWidth: true }
            }
        }
    }

    HistoryDialog { id: historyDialog }
    ConfirmDialog {
        id: reopenDialog
        title: "Riaprire la gara?"
        body: "Il risultato proclamato verrà annullato e la configurazione tornerà modificabile. Voti e storico restano."
        confirmText: "Riapri gara"
        onConfirmed: manche.reopen()
    }
}
