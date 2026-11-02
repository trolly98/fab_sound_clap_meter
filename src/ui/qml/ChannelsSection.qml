import QtQuick
import QtQuick.Controls

SectionCard {
    title: "Ingressi audio"
    Repeater {
        model: clapMeter.channels
        ChannelCard {
            required property var modelData
            required property int index
            channel: modelData
            channelIndex: index
        }
    }
    Button { text: "Aggiungi ingresso"; onClicked: clapMeter.addChannel() }
}
