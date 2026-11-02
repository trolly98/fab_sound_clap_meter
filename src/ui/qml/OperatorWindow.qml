import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    width: 1200; height: 820
    visible: true
    title: "Applausometro - Operatore"
    Material.theme: Material.Dark

    PublicWindow { id: publicView; visible: true }

    header: TabBar {
        id: tabs
        TabButton { text: "Configurazione" }
        TabButton { text: "Manche" }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: tabs.currentIndex
        ConfigurationTab { publicView: publicView }
        MancheTab {}
    }
}
