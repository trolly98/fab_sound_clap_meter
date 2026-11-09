import QtQuick
import QtQuick.Layouts

// Barra pulsanti per le finestre: i Button vanno dichiarati dentro, allineati a destra.
Item {
    default property alias buttons: row.data
    implicitHeight: row.implicitHeight + 20
    RowLayout {
        id: row
        anchors { right: parent.right; verticalCenter: parent.verticalCenter; rightMargin: 16 }
        spacing: 8
    }
}
