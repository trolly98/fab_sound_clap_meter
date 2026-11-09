import QtQuick
import QtQuick.Controls

Dialog {
    modal: true
    anchors.centerIn: Overlay.overlay
    width: 520          // fissa: una larghezza calcolata dalla finestra genera un binding loop nelle finestre Material
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
}
