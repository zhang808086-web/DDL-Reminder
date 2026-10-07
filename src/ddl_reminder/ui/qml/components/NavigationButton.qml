import QtQuick
import QtQuick.Controls.Basic
import ".." as App

Button {
    id: control
    property string iconText: ""
    property bool selected: false
    signal selectedRequested()
    implicitHeight: 46
    checkable: true
    checked: selected
    onClicked: selectedRequested()

    contentItem: Row {
        spacing: 12
        x: 14
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: control.iconText
            color: control.selected ? App.Theme.cyan : App.Theme.textMuted
            font.family: "Segoe UI Symbol"
            font.pixelSize: 16
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: control.text
            color: control.selected ? App.Theme.textPrimary : App.Theme.textSecondary
            font.family: App.Theme.fontFamily
            font.pixelSize: 14
            font.weight: control.selected ? Font.DemiBold : Font.Normal
        }
    }
    background: Rectangle {
        color: control.selected ? App.Theme.cyanDim
              : control.hovered ? App.Theme.surfaceHover : "transparent"
        radius: App.Theme.radiusMedium
        border.color: control.selected ? "#275B75" : "transparent"
    }
}
