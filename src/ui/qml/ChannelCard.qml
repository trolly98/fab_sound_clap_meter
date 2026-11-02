import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Frame {
    id: card
    property QtObject channel: null
    property int channelIndex: 0
    Layout.fillWidth: true

    ColumnLayout {
        anchors.fill: parent
        RowLayout {
            Switch { checked: card.channel.enabled; onToggled: card.channel.enabled = checked }
            ComboBox {
                Layout.fillWidth: true
                model: clapMeter.deviceNames()
                currentIndex: Math.max(0, model.indexOf(card.channel.deviceName))
                onActivated: card.channel.deviceName = currentText
            }
            Button { text: "Rimuovi"; onClicked: clapMeter.removeChannel(card.channelIndex) }
        }
        RowLayout {
            Label { text: "Peso " + card.channel.weight.toFixed(1) }
            Slider {
                Layout.fillWidth: true
                from: 1; to: 10; stepSize: 0.5
                value: card.channel.weight
                onMoved: card.channel.weight = value
            }
        }
        LiveDbBar {
            Layout.fillWidth: true
            db: card.channel.levelDb
            floorDb: clapMeter.floorDb; peakDb: clapMeter.peakDb
        }
    }
}
