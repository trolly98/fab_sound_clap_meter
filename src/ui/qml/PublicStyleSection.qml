import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SectionCard {
    property var publicView: null
    title: "Stile pubblico"

    ComboBox {
        Layout.fillWidth: true
        model: clapMeter.styleNames
        currentIndex: model.indexOf(clapMeter.styleName)
        onActivated: clapMeter.setStyle(currentText)
    }
    RowLayout {
        Button { text: publicView && publicView.visible ? "Nascondi pubblico" : "Mostra pubblico"; onClicked: publicView.visible = !publicView.visible }
        Button { text: "Schermo intero"; onClicked: { publicView.visible = true; publicView.toggleFullScreen() } }
    }
}
