import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Un parametro regolabile di un algoritmo (etichetta + cursore), costruito dalla sua descrizione.
ColumnLayout {
    id: root
    property var parameter: null
    Layout.fillWidth: true

    Label {
        text: root.parameter.label + ": " + slider.value.toFixed(root.parameter.step < 1 ? 1 : 0) + " " + root.parameter.unit
    }
    Slider {
        id: slider
        Layout.fillWidth: true
        from: root.parameter.minimum; to: root.parameter.maximum; stepSize: root.parameter.step
        value: root.parameter.value
        onMoved: clapMeter.applause.setParameter(root.parameter.key, value)
    }
}
