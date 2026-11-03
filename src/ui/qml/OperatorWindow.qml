import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    width: 1200; height: 820
    visible: true
    title: "Applausometro - Operatore"
    Material.theme: Material.Dark
    Material.background: Theme.colors.windowColor
    Material.foreground: Theme.colors.textPrimary
    Material.accent: Theme.colors.controlAccent
    Material.primary: Theme.colors.headerColor

    // L'unico punto in cui si carica la palette scelta: operatore e pubblico la leggono da Theme.colors
    Loader {
        source: clapMeter.paletteUrl
        onLoaded: Theme.colors = item
    }

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
