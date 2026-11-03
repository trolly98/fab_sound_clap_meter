import QtQuick

Item {
    id: root
    property real db: -100
    property real floorDb: -100
    property real peakDb: 0
    readonly property real minDb: -80
    function pos(v) { return width * Math.min(1, Math.max(0, (v - minDb) / -minDb)) }

    implicitHeight: 28
    Rectangle { anchors.fill: parent; radius: 4; color: Theme.colors.meterTrack }
    Rectangle { width: root.pos(root.db); height: parent.height; radius: 4; color: Theme.colors.meterFill }
    Rectangle { x: root.pos(root.floorDb); width: 2; height: parent.height; color: Theme.colors.markerLow }
    Rectangle { x: root.pos(root.peakDb); width: 2; height: parent.height; color: Theme.colors.markerHigh }
    Text {
        anchors.centerIn: parent
        text: root.db.toFixed(1) + " dB"
        color: Theme.colors.textPrimary
        style: Text.Outline; styleColor: Theme.colors.meterTrack   // leggibile sia sul riempimento sia sul fondo
    }
}
