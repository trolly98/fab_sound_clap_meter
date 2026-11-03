pragma Singleton
import QtQuick
import "palettes"

// Tavolozza attiva, condivisa da operatore e pubblico. La imposta OperatorWindow quando cambia la palette.
QtObject {
    property QtObject colors: DefaultPalette {}
}
