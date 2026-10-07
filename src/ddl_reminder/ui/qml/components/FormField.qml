import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App

ColumnLayout {
    id: field
    property string label: ""
    property alias text: input.text
    property alias placeholderText: input.placeholderText
    property int maximumLength: 32767
    property bool multiline: false
    spacing: 7

    Text {
        text: field.label
        color: App.Theme.textSecondary
        font.family: App.Theme.fontFamily
        font.pixelSize: 12
        font.weight: Font.DemiBold
    }

    TextArea {
        id: input
        Layout.fillWidth: true
        Layout.preferredHeight: field.multiline ? 96 : 44
        color: App.Theme.textPrimary
        placeholderTextColor: App.Theme.textMuted
        font.family: App.Theme.fontFamily
        font.pixelSize: 13
        wrapMode: field.multiline ? TextEdit.Wrap : TextEdit.NoWrap
        selectByMouse: true
        leftPadding: 14
        rightPadding: 14
        topPadding: field.multiline ? 12 : 11
        background: Rectangle {
            color: App.Theme.surface
            radius: App.Theme.radiusMedium
            border.color: input.activeFocus ? App.Theme.cyan : App.Theme.border
            border.width: 1
        }
        onTextChanged: {
            if (text.length > field.maximumLength)
                text = text.slice(0, field.maximumLength)
        }
    }
}
