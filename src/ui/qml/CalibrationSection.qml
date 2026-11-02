import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SectionCard {
    title: "Calibrazione"

    ComboBox {
        Layout.fillWidth: true
        model: clapMeter.modeLabels
        currentIndex: clapMeter.modeIndex
        onActivated: clapMeter.setModeIndex(currentIndex)
    }
    LiveDbBar {
        Layout.fillWidth: true
        db: clapMeter.combinedDb
        floorDb: clapMeter.floorDb; peakDb: clapMeter.peakDb
    }
    RowLayout {
        visible: clapMeter.usesCapture
        Button { text: "Cattura fondo (=1)"; enabled: clapMeter.captureLabel === ""; onClicked: clapMeter.captureFloor() }
        Button { text: "Cattura applauso (=10)"; enabled: clapMeter.captureLabel === ""; onClicked: clapMeter.capturePeak() }
    }
    Label { visible: clapMeter.captureLabel !== ""; text: clapMeter.captureLabel }

    Label { text: "Soglia 1:  " + clapMeter.floorDb.toFixed(1) + " dB" }
    Slider { Layout.fillWidth: true; from: -80; to: 0; value: clapMeter.floorDb; onMoved: clapMeter.setFloorDb(value) }
    Label { text: "Soglia 10: " + clapMeter.peakDb.toFixed(1) + " dB" }
    Slider { Layout.fillWidth: true; from: -80; to: 0; value: clapMeter.peakDb; onMoved: clapMeter.setPeakDb(value) }
    Label { visible: clapMeter.usesCurve; text: "Curva (esponente): " + clapMeter.curveExponent.toFixed(2) }
    Slider { visible: clapMeter.usesCurve; Layout.fillWidth: true; from: 0.3; to: 3; value: clapMeter.curveExponent; onMoved: clapMeter.setCurveExponent(value) }

    CheckBox {
        text: "Spike filter"
        checked: clapMeter.spikeFilterEnabled
        onToggled: clapMeter.setSpikeFilterEnabled(checked)
    }
    Label {
        Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.7; font.pixelSize: 12
        text: "Toglie i picchi brevi (colpi sul microfono, urla, battiti isolati). Gli applausi veri restano. Ritarda la misura."
    }
    Label { visible: clapMeter.spikeFilterEnabled; text: "Soglia spike: " + clapMeter.spikeThresholdDb.toFixed(0) + " dB sopra il livello normale" }
    Slider {
        visible: clapMeter.spikeFilterEnabled
        Layout.fillWidth: true; from: 6; to: 30; stepSize: 1
        value: clapMeter.spikeThresholdDb
        onMoved: clapMeter.setSpikeThresholdDb(value)
    }
    Label { visible: clapMeter.spikeFilterEnabled; text: "Durata massima spike: " + clapMeter.spikeMaxDurationMs.toFixed(0) + " ms (piu' lungo = applauso)" }
    Slider {
        visible: clapMeter.spikeFilterEnabled
        Layout.fillWidth: true; from: 100; to: 800; stepSize: 50
        value: clapMeter.spikeMaxDurationMs
        onMoved: clapMeter.setSpikeMaxDurationMs(value)
    }
    Label {
        visible: clapMeter.spikeFilterEnabled; opacity: 0.7; font.pixelSize: 12
        text: "Ritardo della misura: " + (clapMeter.spikeDelayMs / 1000).toFixed(1) + " s"
    }
}
