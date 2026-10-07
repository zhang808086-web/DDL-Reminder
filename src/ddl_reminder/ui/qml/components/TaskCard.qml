import QtQuick
import QtQuick.Controls.Basic
import ".." as App

Rectangle {
    id: card
    objectName: "taskCard"
    required property int taskId
    required property string title
    required property string description
    required property string deadlineText
    required property string remainingText
    required property string category
    required property bool completed
    signal openRequested(int taskId)
    signal completeRequested(int taskId)

    implicitHeight: description.length > 0 ? 112 : 94
    radius: App.Theme.radiusLarge
    color: mouseArea.containsMouse ? App.Theme.surfaceHover : App.Theme.surfaceRaised
    border.color: mouseArea.containsMouse ? "#38527A" : App.Theme.borderSoft
    border.width: 1

    Rectangle {
        width: 3
        height: parent.height - 28
        anchors.left: parent.left
        anchors.leftMargin: 1
        anchors.verticalCenter: parent.verticalCenter
        radius: 2
        color: card.completed ? App.Theme.success : status.tone
    }

    Column {
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.right: status.left
        anchors.rightMargin: 18
        anchors.verticalCenter: parent.verticalCenter
        spacing: 6
        Text {
            width: parent.width
            text: card.title
            color: App.Theme.textPrimary
            elide: Text.ElideRight
            font.family: App.Theme.fontFamily
            font.pixelSize: 16
            font.weight: Font.DemiBold
        }
        Text {
            width: parent.width
            visible: card.description.length > 0
            text: card.description
            color: App.Theme.textSecondary
            elide: Text.ElideRight
            font.family: App.Theme.fontFamily
            font.pixelSize: 12
        }
        Text {
            text: card.deadlineText
            color: App.Theme.textMuted
            font.family: App.Theme.fontFamily
            font.pixelSize: 12
        }
    }

    StatusChip {
        id: status
        objectName: "taskStatusChip"
        anchors.right: card.completed ? parent.right : completeBox.left
        anchors.rightMargin: card.completed ? 18 : 14
        anchors.verticalCenter: parent.verticalCenter
        category: card.category
        label: card.remainingText
    }

    CheckBox {
        id: completeBox
        objectName: "completionAction"
        anchors.right: parent.right
        anchors.rightMargin: 18
        anchors.verticalCenter: parent.verticalCenter
        checked: card.completed
        visible: !card.completed
        width: 34
        height: 34
        indicator: Rectangle {
            anchors.centerIn: parent
            width: 30
            height: 30
            radius: 15
            color: completeBox.hovered ? "#173F38" : "#102B29"
            border.color: "#275D50"
            Text {
                anchors.centerIn: parent
                text: "✓"
                color: App.Theme.success
                font.pixelSize: 15
                font.bold: true
            }
        }
        contentItem: Item {}
        onClicked: card.completeRequested(card.taskId)
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        anchors.rightMargin: card.completed ? 0 : 58
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: card.openRequested(card.taskId)
    }
}
