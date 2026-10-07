import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App
import "../components"

Dialog {
    id: dialog
    objectName: "taskDetailDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 500
    modal: true
    padding: 0
    property int taskId: -1
    property string taskTitle: ""
    property string description: ""
    property string dateText: ""
    property string timeText: ""
    property bool completed: false
    signal editRequested(var details)
    signal deleteRequested(int taskId, string taskTitle)

    function detailsMap() {
        return {
            "taskId": taskId,
            "title": taskTitle,
            "description": description,
            "dateText": dateText,
            "timeText": timeText,
            "completed": completed
        }
    }
    function openForTask(id) {
        var details = appController.taskDetails(id)
        if (!details || details.taskId === undefined)
            return
        taskId = details.taskId
        taskTitle = details.title
        description = details.description
        dateText = details.dateText
        timeText = details.timeText
        completed = details.completed
        open()
    }

    background: Rectangle {
        color: App.Theme.surfaceRaised
        radius: App.Theme.radiusPanel
        border.color: App.Theme.border
    }
    contentItem: ColumnLayout {
        spacing: 18
        anchors.margins: 26
        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: "任务详情"
                color: App.Theme.textMuted
                font.family: App.Theme.fontFamily
                font.pixelSize: 12
                font.weight: Font.DemiBold
                font.letterSpacing: 1.2
            }
            WindowButton { text: "×"; onClicked: dialog.close() }
        }
        Text {
            Layout.fillWidth: true
            text: dialog.taskTitle
            color: App.Theme.textPrimary
            wrapMode: Text.Wrap
            font.family: App.Theme.fontFamily
            font.pixelSize: 23
            font.weight: Font.Bold
        }
        Text {
            Layout.fillWidth: true
            visible: dialog.description.length > 0
            text: dialog.description
            color: App.Theme.textSecondary
            wrapMode: Text.Wrap
            font.family: App.Theme.fontFamily
            font.pixelSize: 13
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 66
            radius: App.Theme.radiusMedium
            color: App.Theme.surface
            border.color: App.Theme.borderSoft
            Row {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                spacing: 12
                Text { text: "◷"; color: App.Theme.cyan; font.pixelSize: 20 }
                Column {
                    spacing: 3
                    Text { text: "截止时间"; color: App.Theme.textMuted; font.family: App.Theme.fontFamily; font.pixelSize: 10 }
                    Text { text: dialog.dateText + "  " + dialog.timeText; color: App.Theme.textPrimary; font.family: App.Theme.fontFamily; font.pixelSize: 14; font.weight: Font.DemiBold }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            AppButton {
                text: "删除"
                danger: true
                onClicked: dialog.deleteRequested(dialog.taskId, dialog.taskTitle)
            }
            Item { Layout.fillWidth: true }
            AppButton {
                text: "编辑"
                onClicked: {
                    var details = dialog.detailsMap()
                    dialog.close()
                    dialog.editRequested(details)
                }
            }
            AppButton {
                text: dialog.completed ? "恢复任务" : "标记完成"
                primary: true
                onClicked: {
                    var succeeded = dialog.completed
                        ? appController.restoreTask(dialog.taskId)
                        : appController.completeTask(dialog.taskId)
                    if (succeeded)
                        dialog.close()
                }
            }
        }
    }
}
