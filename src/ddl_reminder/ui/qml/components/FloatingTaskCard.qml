import QtQuick
import QtQuick.Controls.Basic
import ".." as App

Rectangle {
    id: card
    required property int taskId
    required property string title
    required property string remainingText
    required property string category
    signal openRequested(int taskId)
    signal completeRequested(int taskId)

    implicitHeight: 88
    radius: App.Theme.radiusMedium
    color: hoverArea.containsMouse ? App.Theme.surfaceHover : App.Theme.surfaceRaised
    border.color: App.Theme.borderSoft

    Column {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: completeButton.left
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        spacing: 9
        Text {
            width: parent.width
            text: card.title
            color: App.Theme.textPrimary
            elide: Text.ElideRight
            font.family: App.Theme.fontFamily
            font.pixelSize: 14
            font.weight: Font.DemiBold
        }
        StatusChip { category: card.category; label: card.remainingText }
    }

    Button {
        id: completeButton
        anchors.right: parent.right
        anchors.rightMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        width: 32
        height: 32
        contentItem: Text {
            text: "✓"
            color: App.Theme.success
            font.pixelSize: 16
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: 16
            color: completeButton.hovered ? "#173F38" : "#102B29"
            border.color: "#275D50"
        }
        onClicked: card.completeRequested(card.taskId)
    }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        anchors.rightMargin: 54
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: card.openRequested(card.taskId)
    }
}
