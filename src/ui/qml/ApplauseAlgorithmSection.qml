import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SectionCard {
    title: "Applause Algorithm"
    // I parametri arrivano dall'algoritmo scelto: ognuno dichiara se e' "advanced".
    readonly property var basicParameters: clapMeter.applause.parameters.filter(p => !p.advanced)
    readonly property var advancedParameters: clapMeter.applause.parameters.filter(p => p.advanced)

    ComboBox {
        Layout.fillWidth: true
        model: clapMeter.applause.algorithmNames
        currentIndex: Math.max(0, model.indexOf(clapMeter.applause.algorithmName))
        onActivated: clapMeter.applause.selectAlgorithm(currentText)
    }
    Repeater {
        model: basicParameters
        ParameterSlider { required property var modelData; parameter: modelData }
    }
    AdvancedGroup {
        visible: advancedParameters.length > 0
        Repeater {
            model: advancedParameters
            ParameterSlider { required property var modelData; parameter: modelData }
        }
    }
}
