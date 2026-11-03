import QtQuick
import "../palettes"

// CONTRATTO DEGLI STILI PUBBLICO
// Ogni stile eredita da questo file e disegna soltanto. Valori disponibili (arrivano da `meter`):
//   actualScore   voto live 1-10 (alias: score)    scoreText   "7.3"
//   maxScore / minScore       massimo e minimo raggiunti    scaleMax / scaleMin   limiti della scala
//   applauseScore             risultato dell'Applause Algorithm (live)
//   applauseFinalScore        risultato finale congelato allo stop    applauseRunning   analisi in corso
//   progress 0..1             actualScore sulla scala        combinedDb  livello in dB
//   colors                    palette scelta (vedi palettes/ScorePaletteBase.qml): niente colori nel codice dello stile
//   meter.floorDb / peakDb / channels[i].{deviceName, weight, levelDb, enabled}  per usi avanzati
// Nuovo stile: copia BarStyle.qml in <Nome>Style.qml, viene scoperto da solo.
Item {
    property QtObject meter: null
    property QtObject colors: DefaultPalette {}   // sostituita dalla palette scelta dall'operatore
    readonly property real actualScore: meter ? meter.actual_score : 1.0
    readonly property real score: actualScore
    readonly property string scoreText: meter ? meter.scoreText : "1.0"
    readonly property real maxScore: meter ? meter.max_score : 1.0
    readonly property real minScore: meter ? meter.min_score : 1.0
    readonly property real scaleMax: meter ? meter.scale_max : 10.0
    readonly property real scaleMin: meter ? meter.scale_min : 1.0
    readonly property real applauseScore: meter ? meter.applause_score : 1.0
    readonly property real applauseFinalScore: meter ? meter.applause_final_score : 1.0
    readonly property bool applauseRunning: meter ? meter.applause_running : false
    readonly property real progress: (actualScore - scaleMin) / (scaleMax - scaleMin)
    readonly property real combinedDb: meter ? meter.combinedDb : -100
}
