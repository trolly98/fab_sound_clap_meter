import QtQuick

Item {
    id: root
    property real db: -100
    property real floorDb: -100
    property real peakDb: 0
    readonly property real minDb: -80
    function pos(v) { return width * Math.min(1, Math.max(0, (v - minDb) / -minDb)) }

    implicitHeight: 28
    Rectangle { anchors.fill: parent; radius: 4; color: "#2a2a36" }
    Rectangle { width: root.pos(root.db); height: parent.height; radius: 4; color: "#4caf50" }
    Rectangle { x: root.pos(root.floorDb); width: 2; height: parent.height; color: "#2196f3" }
    Rectangle { x: root.pos(root.peakDb); width: 2; height: parent.height; color: "#f44336" }
    Text { anchors.centerIn: parent; color: "white"; text: root.db.toFixed(1) + " dB" }
}
