import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "." as App
import "components"

Window {
    id: root
    objectName: "floatingWindow"
    width: 320
    height: 440
    visible: false
    color: "transparent"
    title: "DDL Reminder"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
    signal taskOpenRequested(int taskId)

    function showWindow() { floatingWindowController.showFromTray() }
    function prepareToQuit() {
        floatingWindowController.savePosition()
        floatingWindowController.allowClose()
        close()
    }

    Component.onCompleted: floatingWindowController.attachWindow(root)

    Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
    Behavior on y { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: 24
        color: "#F20D1426"
        border.color: floatingWindowController.collapsed ? App.Theme.cyan : App.Theme.border
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 14

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                RowLayout {
                    anchors.fill: parent
                    Text {
                        Layout.fillWidth: true
                        text: "NEXT DEADLINES"
                        color: App.Theme.textPrimary
                        font.family: App.Theme.fontFamily
                        font.pixelSize: 13
                        font.weight: Font.Bold
                        font.letterSpacing: 1.1
                    }
                    WindowButton {
                        text: floatingWindowController.pinned ? "◆" : "◇"
                        onClicked: floatingWindowController.togglePinned()
                    }
                    WindowButton { text: "×"; onClicked: floatingWindowController.hideWindow() }
                }
                MouseArea {
                    anchors.fill: parent
                    anchors.rightMargin: 88
                    onPressed: {
                        floatingWindowController.beginDrag()
                        root.startSystemMove()
                    }
                    onReleased: floatingWindowController.finishDrag()
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: App.Theme.borderSoft }

            ListView {
                id: floatingList
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 10
                clip: true
                model: appController.floatingModel
                delegate: FloatingTaskCard {
                    width: floatingList.width
                    onOpenRequested: root.taskOpenRequested(taskId)
                    onCompleteRequested: appController.completeTask(taskId)
                }
                Text {
                    anchors.centerIn: parent
                    visible: floatingList.count === 0
                    text: "暂无未完成任务"
                    color: App.Theme.textMuted
                    font.family: App.Theme.fontFamily
                    font.pixelSize: 13
                }
            }
        }
    }
}
