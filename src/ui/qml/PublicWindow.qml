import QtQuick
import QtQuick.Window

Window {
    id: window
    width: 1280; height: 720
    title: "Applausometro - Pubblico"
    color: Theme.colors.background

    function toggleFullScreen() {
        visibility = visibility === Window.FullScreen ? Window.Windowed : Window.FullScreen
    }

    // La palette scelta dall'operatore (Theme.colors) viene passata allo stile, qualunque esso sia.
    Connections {
        target: Theme
        function onColorsChanged() { if (style.item) style.item.colors = Theme.colors }
    }
    Loader {
        id: style
        anchors.fill: parent
        source: clapMeter.styleUrl
        onLoaded: {
            item.meter = clapMeter
            item.colors = Theme.colors
        }
    }

    MouseArea { anchors.fill: parent; onDoubleClicked: window.toggleFullScreen() }
    Shortcut { sequence: "F11"; onActivated: window.toggleFullScreen() }
}
