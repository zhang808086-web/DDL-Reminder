import QtQuick
import QtQuick.Controls.Basic
import ".." as App

Button {
    id: control
    property bool primary: false
    property bool danger: false

    implicitHeight: 40
    implicitWidth: 112
    font.family: App.Theme.fontFamily
    font.pixelSize: 13
    font.weight: Font.DemiBold
    leftPadding: 18
    rightPadding: 18

    contentItem: Text {
        text: control.text
        color: control.danger ? App.Theme.danger
              : control.primary ? App.Theme.canvas : App.Theme.textPrimary
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: App.Theme.radiusMedium
        color: control.primary ? (control.hovered ? "#74E2FF" : App.Theme.cyan)
              : control.hovered ? App.Theme.surfaceHover : App.Theme.surfaceRaised
        border.color: control.primary ? "transparent"
                      : control.danger ? "#5A2A3B" : App.Theme.border
        border.width: 1
    }
}
