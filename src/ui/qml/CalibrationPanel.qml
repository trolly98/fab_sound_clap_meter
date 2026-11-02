import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

GroupBox {
    title: "Calibration"
    Layout.fillWidth: true

    ColumnLayout {
        anchors.fill: parent
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
            Label { text: clapMeter.captureLabel }
        }
        Label { text: "Soglia 1:  " + clapMeter.floorDb.toFixed(1) + " dB" }
        Slider { Layout.fillWidth: true; from: -80; to: 0; value: clapMeter.floorDb; onMoved: clapMeter.setFloorDb(value) }
        Label { text: "Soglia 10: " + clapMeter.peakDb.toFixed(1) + " dB" }
        Slider { Layout.fillWidth: true; from: -80; to: 0; value: clapMeter.peakDb; onMoved: clapMeter.setPeakDb(value) }
        Label { visible: clapMeter.usesCurve; text: "Curva (esponente): " + clapMeter.curveExponent.toFixed(2) }
        Slider { visible: clapMeter.usesCurve; Layout.fillWidth: true; from: 0.3; to: 3; value: clapMeter.curveExponent; onMoved: clapMeter.setCurveExponent(value) }
    }
}
