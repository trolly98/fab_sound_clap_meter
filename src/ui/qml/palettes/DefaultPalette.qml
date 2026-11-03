import QtQuick

// I colori originali dell'app: scala dal verde (1) al rosso (10), sfondo scuro, testo bianco.
ScorePaletteBase {
    background: "#0b0b12"
    track: "#262633"
    textPrimary: "white"
    accent: "#ffd54f"
    inactiveOpacity: 0.12
    contrastThreshold: 2.0
    // Pannello operatore: come prima di introdurre le palette
    windowColor: "#1c1b1f"
    headerColor: "#1c1b1f"
    surface: "#262633"
    border: "#3a3a52"
    controlAccent: "#f48fb1"
    meterTrack: "#2a2a36"
    meterFill: "#4caf50"
    markerLow: "#2196f3"
    markerHigh: "#f44336"
    scaleStops: {
        var stops = []
        for (var i = 0; i < 10; i++)
            stops.push(Qt.hsla(0.33 - 0.33 * i / 9, 0.9, 0.5, 1))
        return stops
    }
}
