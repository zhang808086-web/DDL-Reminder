import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App
import "../components"

Dialog {
    id: dialog
    objectName: "confirmDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 430
    modal: true
    padding: 0
    property string heading: "请确认"
    property string message: ""
    property string confirmText: "确认"
    property bool dangerous: false
    property var action

    function ask(titleText, bodyText, buttonText, isDangerous, callback) {
        heading = titleText
        message = bodyText
        confirmText = buttonText
        dangerous = isDangerous
        action = callback
        open()
    }

    background: Rectangle {
        color: App.Theme.surfaceRaised
        radius: App.Theme.radiusPanel
        border.color: dialog.dangerous ? "#633244" : App.Theme.border
    }
    contentItem: ColumnLayout {
        spacing: 18
        anchors.margins: 26
        Text {
            text: dialog.heading
            color: App.Theme.textPrimary
            font.family: App.Theme.fontFamily
            font.pixelSize: 19
            font.weight: Font.Bold
        }
        Text {
            Layout.fillWidth: true
            text: dialog.message
            color: App.Theme.textSecondary
            wrapMode: Text.Wrap
            font.family: App.Theme.fontFamily
            font.pixelSize: 13
        }
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            AppButton { text: "取消"; onClicked: dialog.close() }
            AppButton {
                text: dialog.confirmText
                danger: dialog.dangerous
                primary: !dialog.dangerous
                onClicked: {
                    var callback = dialog.action
                    dialog.close()
                    if (callback)
                        callback()
                }
            }
        }
    }
}
