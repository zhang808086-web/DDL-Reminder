import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App
import "../components"

Dialog {
    id: dialog
    objectName: "settingsDialog"
    parent: Overlay.overlay
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)
    width: Math.min(470, parent.width - 48)
    modal: true
    padding: 26

    function showSettings() { open() }

    background: Rectangle {
        color: App.Theme.surfaceRaised
        radius: App.Theme.radiusPanel
        border.color: App.Theme.border
    }
    contentItem: ColumnLayout {
        spacing: 20
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
        Text {
            text: "当前版本 " + updateController.currentVersion + " · " + updateController.status
            color: App.Theme.textSecondary
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.family: App.Theme.fontFamily
            font.pixelSize: 12
        }
        RowLayout {
            Layout.fillWidth: true
            AppButton {
                text: updateController.checking ? "检查中…" : "检查更新"
                enabled: !updateController.checking
                onClicked: updateController.checkNow()
            }
            AppButton {
                visible: updateController.hasUpdate
                text: "下载新版"
                onClicked: updateController.openDownload()
            }
            Item { Layout.fillWidth: true }
            AppButton { text: "完成"; primary: true; onClicked: dialog.close() }
        }
    }
}
