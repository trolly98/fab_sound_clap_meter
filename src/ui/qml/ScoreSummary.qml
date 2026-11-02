import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    spacing: 24
    Label { text: clapMeter.scoreText; font.pixelSize: 72; font.bold: true }
    ColumnLayout {
        Label {
            text: "Min " + clapMeter.min_score.toFixed(1) + "   Max " + clapMeter.max_score.toFixed(1)
                  + "   (scala " + clapMeter.scale_min.toFixed(0) + "-" + clapMeter.scale_max.toFixed(0) + ")"
        }
        Label {
            text: "Applause score " + clapMeter.applause_score.toFixed(1)
                  + (clapMeter.applause_running ? "  (analisi in corso)" : "")
        }
    }
    Button { text: "Azzera min/max"; onClicked: clapMeter.resetExtremes() }
    Item { Layout.fillWidth: true }
}
