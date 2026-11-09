import QtQuick

// Porpora Style
//   Viola scuro  #35246D  sfondo               Bianco panna #F2E8D8  numeri e scritte
//   Viola        #5D5AAA  parti vuote          Chartreuse   #D2D53F  risultato Applause
//   Scala del voto: Rosa #FF9CD9 -> Arancio bruciato #D85A38 -> Giallo caldo #E6E457
// Sulla scala (chiara) il testo e' viola scuro; sullo sfondo (scuro) e' bianco panna.
ScorePaletteBase {
    background: "#35246D"
    track: "#5D5AAA"
    textPrimary: "#F2E8D8"
    accent: "#D2D53F"
    inactiveOpacity: 0.55
    inactiveUsesTrack: true
    contrastThreshold: 0.45
    // Pannello operatore
    windowColor: "#35246D"                 // Viola scuro
    headerColor: Qt.darker(background, 1.25)
    surface: Qt.lighter(background, 1.2)
    border: "#5D5AAA"                      // Viola
    controlAccent: "#FF9CD9"               // Rosa: cursori, interruttori, scheda attiva
    meterTrack: Qt.darker(background, 1.3)
    meterFill: "#E6E457"                   // Giallo caldo
    markerLow: "#FF9CD9"                   // Rosa
    markerHigh: "#D85A38"                  // Arancio bruciato
    // Scheda Manche
    personA: "#FF9CD9"                     // Rosa
    personB: "#D2D53F"                     // Chartreuse
    good: "#E6E457"                        // Giallo caldo
    warn: "#D85A38"                        // Arancio bruciato
    danger: "#D85A38"
    scaleStops: ["#FF9CD9", "#D85A38", "#E6E457"]
}
