import QtQuick
import QtQuick.Controls.Basic
import ".." as App

Button {
    id: control
    property bool destructive: false
    implicitWidth: 42
    implicitHeight: 34
    flat: true

    contentItem: Text {
        text: control.text
        color: control.hovered && control.destructive ? "white" : App.Theme.textSecondary
        font.family: "Segoe UI Symbol"
        font.pixelSize: 15
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        color: control.hovered
               ? (control.destructive ? App.Theme.danger : App.Theme.surfaceHover)
               : "transparent"
        radius: App.Theme.radiusSmall
    }
}
