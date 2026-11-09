import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Item {
    id: root
    readonly property var v: manche.view
    readonly property var config: v.config
    readonly property var sel: config.selected
    readonly property string selId: sel ? sel.id : ""
    readonly property bool editable: !v.locked

    function askCount(count) {
        if (!sel || count === sel.count) return
        var impact = manche.previewCount(sel.id, count)
        if (!impact.needsChoice && impact.removed === 0) { manche.setRoundCount(sel.id, count, "adapt"); return }
        countDialog.roundId = sel.id; countDialog.count = count
        countDialog.removed = impact.removed; countDialog.needsChoice = impact.needsChoice
        countDialog.open()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Rectangle {
            visible: root.v.lockReason !== ""
            Layout.fillWidth: true; implicitHeight: lockLabel.implicitHeight + 16; radius: 8
            color: "transparent"; border.color: Theme.colors.warn
            Label { id: lockLabel; anchors.centerIn: parent; text: root.v.lockReason; color: Theme.colors.warn }
        }

        SectionCard {
            Layout.fillWidth: true
            title: "Impostazioni generali dello spettacolo · Sfidanti"
            expanded: false
            RowLayout {
                spacing: 12
                Repeater {
                    model: ["A", "B"]
                    RowLayout {
                        id: nameRow
                        required property string modelData
                        Layout.fillWidth: true; Layout.preferredWidth: 0; Layout.horizontalStretchFactor: 1
                        PersonBadge { person: nameRow.modelData }
                        TextField {
                            id: nameField
                            Layout.fillWidth: true; enabled: root.editable
                            placeholderText: "Concorrente " + nameRow.modelData
                            Binding on text { when: !nameField.activeFocus; value: root.v.names[nameRow.modelData] }
                            onTextEdited: manche.setPersonName(nameRow.modelData, text)
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true; implicitHeight: modelRow.implicitHeight + 20
            radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border
            RowLayout {
                id: modelRow
                anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 14 }
                ColumnLayout {
                    spacing: 0
                    Label { text: "Modello di partenza"; font.pixelSize: 12; opacity: 0.7 }
                    RowLayout {
                        Label { text: root.v.model.name; font.bold: true; font.pixelSize: 18 }
                        Pill { visible: root.v.model.category !== ""; text: root.v.model.category }
                    }
                }
                Item { Layout.fillWidth: true }
                Button { text: "Carica modello…"; flat: true; enabled: !root.v.live; onClicked: modelsDialog.open() }
                Button { text: "Salva come modello…"; flat: true; enabled: root.v.model.canSave; onClicked: saveDialog.open() }
                Button { text: "Aggiorna modello"; flat: true; enabled: root.v.model.canUpdate; onClicked: updateConfirm.open() }
                Button { text: "↶ Annulla"; flat: true; enabled: root.v.canUndo; onClicked: manche.undo() }
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

            // ---------------- elenco manche (35%)
            Rectangle {
                Layout.horizontalStretchFactor: 35; Layout.fillWidth: true; Layout.fillHeight: true
                Layout.preferredWidth: 0
                radius: 10; color: Theme.colors.surface; border.color: Theme.colors.border
                ColumnLayout {
                    anchors { fill: parent; margins: 12 }
                    RowLayout {
                        Label { text: "Elenco manche"; font.bold: true; Layout.fillWidth: true }
                        Button {
                            text: "＋ Aggiungi"; enabled: root.editable; onClicked: addMenu.open()
                            Menu {
                                id: addMenu
                                MenuItem { text: "Nuova manche"; onTriggered: manche.addRound() }
                                MenuItem { text: "Duplica esistente…"; enabled: root.config.rounds.length > 0; onTriggered: duplicateDialog.open() }
                            }
                        }
                    }
                    Label {
                        visible: root.config.rounds.length === 0
                        Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.75
                        text: "Non ci sono manche. Aggiungine una, oppure carica un modello."
                    }
                    Flickable {
                        id: rowsFlick
                        Layout.fillWidth: true; Layout.fillHeight: true
                        clip: true; contentWidth: width; contentHeight: rowsColumn.implicitHeight
                        ScrollBar.vertical: ScrollBar {}
                        Column {
                            id: rowsColumn
                            width: parent.width - 10; spacing: 4
                            Repeater {
                                model: root.config.rounds
                                RoundRow {
                                    required property var modelData
                                    required property int index
                                    width: rowsColumn.width
                                    item: modelData; rowIndex: index; rowCount: root.config.rounds.length
                                    rowPitch: implicitHeight + rowsColumn.spacing; editable: root.editable; scroller: rowsFlick
                                    onSelectRequested: manche.selectConfigRound(modelData.id)
                                    onActiveToggled: function(on) { manche.setRoundActive(modelData.id, on) }
                                    onMoveRequested: function(target) { manche.moveRound(index, target) }
                                    onDuplicateRequested: manche.duplicateRound(modelData.id)
                                    onDeleteRequested: { deleteDialog.roundId = modelData.id; deleteDialog.roundName = modelData.name; deleteDialog.open() }
                                }
                            }
                        }
                    }
                }
            }

            // ---------------- dettaglio della manche selezionata (65%)
            Rectangle {
                Layout.horizontalStretchFactor: 65; Layout.fillWidth: true; Layout.fillHeight: true
                Layout.preferredWidth: 0
                radius: 10; color: "transparent"; border.color: Theme.colors.border

                Loader {
                    anchors { fill: parent; margins: 12 }
                    sourceComponent: root.sel ? detailComponent : emptyComponent
                }
            }
        }
    }

    Component {
        id: emptyComponent
        ColumnLayout {
            spacing: 8
            Item { Layout.fillHeight: true }
            Label { text: "▤"; font.pixelSize: 44; opacity: 0.5; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Seleziona una manche"; font.pixelSize: 20; font.bold: true; Layout.alignment: Qt.AlignHCenter }
            Label {
                text: "Scegli una manche dall'elenco per modificarne nome, punteggio e sequenza."
                opacity: 0.7; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true; Layout.leftMargin: 30; Layout.rightMargin: 30
            }
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: detailComponent
        Flickable {
            id: flick
            clip: true; contentWidth: width; contentHeight: column.implicitHeight + 8
            ScrollBar.vertical: ScrollBar {}
            property string watchedId: root.selId
            onWatchedIdChanged: { general.expanded = true; scoring.expanded = true; sequence.expanded = true; contentY = 0 }

            ColumnLayout {
                id: column
                width: flick.width - 14; spacing: 12
                Label { text: root.sel.name; font.pixelSize: 22; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }

                SectionCard {
                    id: general
                    Layout.fillWidth: true; title: "Generale"
                    Label { text: "Nome della manche *" }
                    TextField {
                        id: nameField
                        Layout.fillWidth: true; enabled: root.editable
                        Binding on text { when: !nameField.activeFocus; value: root.sel.name }
                        onTextEdited: manche.setRoundText(root.sel.id, "name", text)
                    }
                    Label { visible: nameField.text.trim() === ""; text: "Il nome è obbligatorio."; color: Theme.colors.danger }
                    Label { text: "Note" }
                    TextArea {
                        id: notesField
                        Layout.fillWidth: true; Layout.preferredHeight: 90; wrapMode: TextArea.Wrap; enabled: root.editable
                        Binding on text { when: !notesField.activeFocus; value: root.sel.notes }
                        onTextChanged: if (activeFocus) manche.setRoundText(root.sel.id, "notes", text)
                    }
                }

                SectionCard {
                    id: scoring
                    Layout.fillWidth: true; title: "Punteggio"
                    Label { text: "Voti per sfidante" }
                    ComboBox {
                        Layout.fillWidth: true; enabled: root.editable && !root.sel.rulesLocked
                        model: root.config.counts
                        currentIndex: root.sel.count - 1
                        onActivated: { root.askCount(model[currentIndex]); currentIndex = Qt.binding(function() { return root.sel.count - 1 }) }
                    }
                    Label { text: "Regola del punteggio" }
                    ComboBox {
                        Layout.fillWidth: true; enabled: root.editable && !root.sel.rulesLocked
                        model: root.config.methods; textRole: "label"
                        currentIndex: root.config.methods.findIndex(function(m) { return m.id === root.sel.method })
                        onActivated: {
                            manche.setRoundMethod(root.sel.id, root.config.methods[currentIndex].id)
                            currentIndex = Qt.binding(function() { return root.config.methods.findIndex(function(m) { return m.id === root.sel.method }) })
                        }
                    }
                    Label {
                        visible: root.sel.rulesLocked; Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.75; font.pixelSize: 12
                        text: "Questa manche ha regole fisse: numero di voti e regola del punteggio non si cambiano."
                    }
                }

                SectionCard {
                    id: sequence
                    Layout.fillWidth: true; title: "Sequenza interventi"
                    ComboBox {
                        Layout.fillWidth: true; enabled: root.editable
                        model: root.config.orders; textRole: "label"
                        currentIndex: root.config.orders.findIndex(function(o) { return o.id === root.sel.order })
                        onActivated: {
                            manche.setRoundOrder(root.sel.id, root.config.orders[currentIndex].id)
                            currentIndex = Qt.binding(function() { return root.config.orders.findIndex(function(o) { return o.id === root.sel.order }) })
                        }
                    }
                    Label {
                        Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.75; font.pixelSize: 12
                        text: "Trascina i turni (⠿) o usa le frecce. Spostando un turno la sequenza diventa personalizzata."
                    }
                    Flow {
                        id: tiles
                        Layout.fillWidth: true; spacing: 8
                        Repeater {
                            model: root.sel.turns
                            TurnTile {
                                required property var modelData
                                required property int index
                                turn: modelData; tileIndex: index; tileCount: root.sel.turns.length; editable: root.editable; scroller: flick
                                perRow: Math.max(1, Math.floor((tiles.width + tiles.spacing) / pitchX))
                                onMoveRequested: function(target) { manche.moveTurn(root.sel.id, index, target) }
                            }
                        }
                    }
                }
            }
        }
    }

    // ---------------- finestre
    ConfirmDialog {
        id: deleteDialog
        property string roundId: ""
        property string roundName: ""
        title: "Eliminare la manche?"
        body: "«" + roundName + "» verrà eliminata insieme ai suoi voti. Puoi annullare con Annulla finché non avvii una misura."
        confirmText: "Elimina"
        onConfirmed: manche.deleteRound(roundId)
    }
    CountDialog { id: countDialog }
    DuplicateRoundDialog { id: duplicateDialog }
    SaveModelDialog { id: saveDialog }
    ModelsDialog {
        id: modelsDialog
        onLoadRequested: function(modelId, modelName) { loadConfirm.modelId = modelId; loadConfirm.modelName = modelName; loadConfirm.open() }
        onDeleteRequested: function(modelId, modelName) { deleteModelConfirm.modelId = modelId; deleteModelConfirm.modelName = modelName; deleteModelConfirm.open() }
    }
    ConfirmDialog {
        id: loadConfirm
        property string modelId: ""
        property string modelName: ""
        title: "Caricare il modello?"
        body: "La gara corrente viene sostituita dal modello «" + modelName + "»: manche, voti e storico ripartono da zero. I nomi dei concorrenti restano."
        confirmText: "Carica"
        onConfirmed: { modelsDialog.close(); manche.loadModel(modelId) }
    }
    ConfirmDialog {
        id: deleteModelConfirm
        property string modelId: ""
        property string modelName: ""
        title: "Eliminare il modello?"
        body: "Il modello «" + modelName + "» verrà eliminato dall'elenco. La gara corrente non cambia."
        confirmText: "Elimina"
        onConfirmed: manche.deleteModel(modelId)
    }
    ConfirmDialog {
        id: updateConfirm
        title: "Aggiornare il modello?"
        body: "Il modello «" + root.v.model.name + "» verrà sovrascritto con le manche di adesso."
        confirmText: "Aggiorna"
        onConfirmed: manche.updateModel()
    }
}
