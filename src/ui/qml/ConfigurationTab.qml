import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var publicView: null
    readonly property int gap: 16
    readonly property int minColumnWidth: 440

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 12

        ScoreSummary { Layout.fillWidth: true }

        Flickable {
            id: flick
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true
            contentWidth: width
            contentHeight: flow.height
            ScrollBar.vertical: ScrollBar {}

            // Layout responsive: il numero di colonne segue la larghezza; ogni sezione si comprime.
            Flow {
                id: flow
                width: flick.width - 14
                spacing: root.gap
                readonly property int columns: Math.max(1, Math.floor((width + spacing) / (root.minColumnWidth + spacing)))
                readonly property real columnWidth: (width - spacing * (columns - 1)) / columns

                ChannelsSection { width: flow.columnWidth }
                CalibrationSection { width: flow.columnWidth }
                ApplauseAlgorithmSection { width: flow.columnWidth }
                PublicStyleSection { width: flow.columnWidth; publicView: root.publicView }
            }
        }
    }
}
