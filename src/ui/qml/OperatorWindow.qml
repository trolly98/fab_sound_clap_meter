import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1100; height: 780
    visible: true
    title: "Operator"
    Material.theme: Material.Dark

    PublicWindow { id: publicWindow; visible: true }

    RowLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 16

        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            Label { text: "Ingressi audio"; font.pixelSize: 20 }
            ScrollView {
                Layout.fillWidth: true; Layout.fillHeight: true
                ColumnLayout {
                    width: parent.width
                    Repeater {
                        model: clapMeter.channels
                        ChannelCard { required property var modelData; required property int index
                                      channel: modelData; channelIndex: index }
                    }
                }
            }
            Button { text: "Aggiungi ingresso"; onClicked: clapMeter.addChannel() }
        }

        ColumnLayout {
            Layout.preferredWidth: 420; Layout.fillHeight: true
            Label { text: clapMeter.scoreText; font.pixelSize: 96; font.bold: true; Layout.alignment: Qt.AlignHCenter }
            CalibrationPanel {}
            RowLayout {
                Label { text: "Stile pubblico" }
                ComboBox {
                    Layout.fillWidth: true
                    model: clapMeter.styleNames
                    currentIndex: model.indexOf(clapMeter.styleName)
                    onActivated: clapMeter.setStyle(currentText)
                }
            }
            RowLayout {
                Button { text: publicWindow.visible ? "Nascondi pubblico" : "Mostra pubblico"; onClicked: publicWindow.visible = !publicWindow.visible }
                Button { text: "Schermo intero"; onClicked: { publicWindow.visible = true; publicWindow.toggleFullScreen() } }
            }
            Item { Layout.fillHeight: true }
        }
    }
}
