import QtQuick
import QtQuick.Controls
import ".."

// Messaggio breve in basso: compare e sparisce da solo.
Rectangle {
    id: root
    function show(message) { label.text = message; opacity = 1; hideTimer.restart() }
    anchors { horizontalCenter: parent.horizontalCenter; bottom: parent.bottom; bottomMargin: 22 }
    z: 100; opacity: 0; visible: opacity > 0
    implicitWidth: label.implicitWidth + 36; implicitHeight: label.implicitHeight + 18
    radius: height / 2; color: Theme.colors.controlAccent
    Behavior on opacity { NumberAnimation { duration: 180 } }
    Label { id: label; anchors.centerIn: parent; color: Theme.colors.contrastText(Theme.colors.controlAccent) }
    Timer { id: hideTimer; interval: 3500; onTriggered: root.opacity = 0 }
}
