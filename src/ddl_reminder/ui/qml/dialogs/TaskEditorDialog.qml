import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import ".." as App
import "../components"

Dialog {
    id: dialog
    objectName: "taskEditorDialog"
    parent: Overlay.overlay
    x: Math.round((parent.width - width) / 2)
    y: Math.round((parent.height - height) / 2)
    width: Math.min(520, parent.width - 48)
    modal: true
    closePolicy: Popup.CloseOnEscape
    padding: 26
    property int taskId: -1
    property bool editing: false

    function todayText() {
        var now = new Date()
        return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0")
               + "-" + String(now.getDate()).padStart(2, "0")
    }
    function openForCreate() {
        editing = false
        taskId = -1
        titleField.text = ""
        descriptionField.text = ""
        deadlineFields.dateText = todayText()
        deadlineFields.timeText = "23:59"
        open()
        titleField.forceActiveFocus()
    }
    function openForTask(details) {
        editing = true
        taskId = details.taskId
        titleField.text = details.title
        descriptionField.text = details.description
        deadlineFields.dateText = details.dateText
        deadlineFields.timeText = details.timeText
        open()
        titleField.forceActiveFocus()
    }
    function save() {
        var succeeded = editing
            ? appController.updateTask(taskId, titleField.text, descriptionField.text,
                                       deadlineFields.dateText, deadlineFields.timeText)
            : appController.createTask(titleField.text, descriptionField.text,
                                       deadlineFields.dateText, deadlineFields.timeText)
        if (succeeded)
            close()
    }

    background: Rectangle {
        color: App.Theme.surfaceRaised
        radius: App.Theme.radiusPanel
        border.color: App.Theme.border
        border.width: 1
    }
    contentItem: ColumnLayout {
        spacing: 18

        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: dialog.editing ? "编辑任务" : "新建任务"
                color: App.Theme.textPrimary
                font.family: App.Theme.fontFamily
                font.pixelSize: 21
                font.weight: Font.Bold
            }
            WindowButton { text: "×"; onClicked: dialog.close() }
        }
        FormField {
            id: titleField
            Layout.fillWidth: true
            label: "任务标题"
            placeholderText: "最多 15 个字符"
            maximumLength: 64
        }
        FormField {
            id: descriptionField
            Layout.fillWidth: true
            label: "说明（可选）"
            placeholderText: "补充任务背景或交付要求"
            multiline: true
        }
        DateTimeField { id: deadlineFields; Layout.fillWidth: true }
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            AppButton { text: "取消"; onClicked: dialog.close() }
            AppButton { text: dialog.editing ? "保存修改" : "创建任务"; primary: true; onClicked: dialog.save() }
        }
    }
}
