import QtQuick
import QtQuick.Window

Window {
    id: window
    width: 1280; height: 720
    title: "Applausometro - Pubblico"
    color: "black"

    function toggleFullScreen() {
        visibility = visibility === Window.FullScreen ? Window.Windowed : Window.FullScreen
    }

    Loader {
        anchors.fill: parent
        source: clapMeter.styleUrl
        onLoaded: item.meter = clapMeter
    }

    MouseArea { anchors.fill: parent; onDoubleClicked: window.toggleFullScreen() }
    Shortcut { sequence: "F11"; onActivated: window.toggleFullScreen() }
}
