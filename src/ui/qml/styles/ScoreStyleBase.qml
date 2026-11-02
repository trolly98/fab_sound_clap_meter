import QtQuick

// CONTRATTO DEGLI STILI PUBBLICO
// Ogni stile eredita da questo file e disegna soltanto. Tutti i dati arrivano da `meter`:
//   meter.score (1.0-10.0)   meter.scoreText ("7.3")   meter.combinedDb
//   meter.floorDb  meter.peakDb  meter.channels[i].{deviceName, weight, levelDb, enabled}
// Per creare un nuovo stile: copia BarStyle.qml in <Nome>Style.qml, viene scoperto da solo.
Item {
    property QtObject meter: null
    readonly property real score: meter ? meter.score : 1.0
    readonly property string scoreText: meter ? meter.scoreText : "1.0"
    readonly property real progress: (score - 1.0) / 9.0
    readonly property real combinedDb: meter ? meter.combinedDb : -100
}
