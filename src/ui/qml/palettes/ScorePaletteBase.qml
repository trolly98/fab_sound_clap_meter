import QtQuick

// CONTRATTO DELLE PALETTE COLORI
// Una palette e' un file <Nome>Palette.qml che eredita da qui e imposta i colori: appare da sola nel menu
// "Color Palette" (il nome si ricava dal file: PorporaStylePalette.qml -> "Porpora Style").
// Ogni stile pubblico legge i colori da `colors` e non ha colori scritti nel codice.
// La stessa palette colora anche il pannello operatore (vedi i ruoli in fondo ai colori).
QtObject {
    property color background: "#0b0b12"   // sfondo dello schermo pubblico
    property color track: "#262633"        // parte "vuota" di quadranti e scale
    property color textPrimary: "white"    // numeri e scritte principali
    property color accent: "#ffd54f"       // risultato dell'Applause Algorithm
    property real inactiveOpacity: 0.12    // quanto si vedono i segmenti spenti (0-1)
    property bool inactiveUsesTrack: false // true: i segmenti spenti usano `track` invece del loro colore sbiadito
    property var scaleStops: []            // colori della scala: dal voto 1 (primo) al 10 (ultimo), interpolati
    // Sopra questa luminosita' (0-1) il testo sopra un colore della scala diventa scuro (come lo sfondo).
    // Un valore sopra 1 = testo sempre chiaro.
    property real contrastThreshold: 2.0

    // --- Pannello operatore (facoltativi: se una palette non li imposta, vengono ricavati dai colori sopra) ---
    property color windowColor: background              // sfondo della finestra operatore
    property color headerColor: windowColor             // barra delle schede in alto
    property color surface: Qt.lighter(background, 1.25) // riquadri delle sezioni
    property color border: Qt.lighter(background, 1.8)  // bordo dei riquadri
    property color controlAccent: accent                // cursori, interruttori, spunte, scheda attiva
    property color meterTrack: Qt.darker(surface, 1.2)  // fondo delle barre dei dB
    property color meterFill: accent                    // riempimento delle barre dei dB
    property color markerLow: scaleColor(0)             // riga della soglia dell'1
    property color markerHigh: scaleColor(1)            // riga della soglia del 10

    // progress: 0 = voto 1, 1 = voto 10
    function scaleColor(progress) {
        var count = scaleStops.length
        if (count === 0) return accent
        if (count === 1) return Qt.color(scaleStops[0])
        var position = Math.min(1, Math.max(0, progress)) * (count - 1)
        var index = Math.min(count - 2, Math.floor(position))
        var fraction = position - index
        var from = Qt.color(scaleStops[index]), to = Qt.color(scaleStops[index + 1])
        return Qt.rgba(from.r + (to.r - from.r) * fraction,
                       from.g + (to.g - from.g) * fraction,
                       from.b + (to.b - from.b) * fraction, 1)
    }

    // Colore del testo da scrivere sopra `fill` per leggerlo bene
    function contrastText(fill) {
        var c = Qt.color(fill)
        var luminance = 0.299 * c.r + 0.587 * c.g + 0.114 * c.b
        return luminance > contrastThreshold ? background : textPrimary
    }
}
