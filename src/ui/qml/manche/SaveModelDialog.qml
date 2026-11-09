import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

AppDialog {
    id: dialog
    title: "Salva come modello"
    property string error: manche.validateModelName(nameField.text)
    property bool touched: false
    onAboutToShow: { nameField.text = ""; descriptionField.text = ""; touched = false; serverError.text = "" }
    function save() {
        var message = manche.saveModel(nameField.text, descriptionField.text)
        if (message) { serverError.text = message } else { dialog.close() }
    }
    contentItem: ColumnLayout {
        spacing: 8
        Label { text: "Le manche di adesso diventano un modello riutilizzabile." ; opacity: 0.75; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Label { text: "Nome del modello *" }
        TextField { id: nameField; Layout.fillWidth: true; onTextEdited: dialog.touched = true }
        Label { visible: dialog.touched && dialog.error !== ""; text: dialog.error; color: Theme.colors.danger }
        Label { id: serverError; color: Theme.colors.danger }
        Label { text: "Descrizione (facoltativa)" }
        TextArea { id: descriptionField; Layout.fillWidth: true; Layout.preferredHeight: 80; wrapMode: TextArea.Wrap }
    }
    footer: DialogButtons {
        Button { text: "Salva"; highlighted: true; enabled: dialog.error === ""; onClicked: dialog.save() }
        Button { text: "Annulla"; onClicked: dialog.close() }
    }
}
