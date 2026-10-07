import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App
import "../components"

Dialog {
    id: dialog
    objectName: "settingsDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 470
    modal: true
    padding: 0

    function showSettings() { open() }

    background: Rectangle {
        color: App.Theme.surfaceRaised
        radius: App.Theme.radiusPanel
        border.color: App.Theme.border
    }
    contentItem: ColumnLayout {
        spacing: 20
        anchors.margins: 26
        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: "设置"
                color: App.Theme.textPrimary
                font.family: App.Theme.fontFamily
                font.pixelSize: 21
                font.weight: Font.Bold
            }
            WindowButton { text: "×"; onClicked: dialog.close() }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 78
            radius: App.Theme.radiusMedium
            color: App.Theme.surface
            border.color: App.Theme.borderSoft
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                Column {
                    Layout.fillWidth: true
                    spacing: 5
                    Text { text: "开机自动启动"; color: App.Theme.textPrimary; font.family: App.Theme.fontFamily; font.pixelSize: 14; font.weight: Font.DemiBold }
                    Text { text: appController.autostartAvailable ? "登录 Windows 后自动运行" : "仅安装版支持此设置"; color: App.Theme.textMuted; font.family: App.Theme.fontFamily; font.pixelSize: 11 }
                }
                Switch {
                    checked: appController.autostartEnabled
                    enabled: appController.autostartAvailable
                    onToggled: appController.setAutostart(checked)
                }
            }
        }
        Text {
            text: "任务数据保存在本机 SQLite 数据库中，升级应用不会清空数据。"
            color: App.Theme.textMuted
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.family: App.Theme.fontFamily
            font.pixelSize: 11
        }
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            AppButton { text: "完成"; primary: true; onClicked: dialog.close() }
        }
    }
}
