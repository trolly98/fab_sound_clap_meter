import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24
        Label { text: "Work in progress"; font.pixelSize: 32; Layout.alignment: Qt.AlignHCenter }

        // Pulsanti provvisori per provare l'analizzatore: le funzioni vere sono nel backend.
        SectionCard {
            title: "Applause analyzer (provvisorio)"
            Layout.preferredWidth: 440
            RowLayout {
                Button { text: "Start applause analyzer"; enabled: !clapMeter.applause_running; onClicked: clapMeter.startApplauseAnalyzer() }
                Button { text: "Stop applause analyzer"; enabled: clapMeter.applause_running; onClicked: clapMeter.stopApplauseAnalyzer() }
            }
            Label { text: "Stato: " + (clapMeter.applause_running ? "in analisi" : "fermo") }
            Label { text: "Applause score live: " + clapMeter.applause_score.toFixed(1) }
            Label { text: "Applause score finale: " + clapMeter.applause_final_score.toFixed(1) }
        }
    }
}
