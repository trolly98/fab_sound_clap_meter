import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "manche"

// Scheda Manche: conduzione della gara, tabellone e configurazione delle manche.
Item {
    id: root
    property int page: 0          // 0 conduzione, 1 tabellone, 2 configurazione

    ColumnLayout {
        anchors { fill: parent; margins: 16 }
        spacing: 12
        MancheHeader { Layout.fillWidth: true }
        TabBar {
            id: tabs
            Layout.fillWidth: true
            onCurrentIndexChanged: root.page = currentIndex
            Binding { target: tabs; property: "currentIndex"; value: root.page }
            TabButton { text: "Conduzione" }
            TabButton { text: "Tabellone" }
            TabButton { text: "Configurazione" }
        }
        StackLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            currentIndex: root.page
            RunPage { onOpenConfig: root.page = 2 }
            BoardPage {}
            ConfigPage {}
        }
    }

    Toast { id: toast }
    Connections {
        target: manche
        function onNotice(message) { toast.show(message) }
        function onPageRequested(name) { root.page = { "run": 0, "board": 1, "config": 2 }[name] }
    }
    Component.onCompleted: if (manche.view.hasResult) root.page = 1
}
