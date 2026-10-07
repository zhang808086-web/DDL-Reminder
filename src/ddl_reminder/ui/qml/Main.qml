import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "." as App
import "components"

ApplicationWindow {
    id: root
    objectName: "mainWindow"
    width: 1180
    height: 760
    minimumWidth: 980
    minimumHeight: 640
    visible: false
    color: App.Theme.canvas
    title: "DDL Reminder"
    flags: Qt.Window | Qt.FramelessWindowHint

    function showMainWindow() {
        root.show()
        root.raise()
        root.requestActivate()
    }

    function showFloatingWindow() {
        // FloatingWindow.qml is composed in the next migration task.
    }

    function prepareToQuit() {
        root.hide()
    }

    Rectangle {
        anchors.fill: parent
        color: App.Theme.canvas
        border.color: App.Theme.border
        border.width: 1
        radius: 16

        RowLayout {
            anchors.fill: parent
            anchors.margins: 1
            spacing: 0

            Rectangle {
                id: sidebar
                objectName: "sidebar"
                Layout.preferredWidth: 238
                Layout.fillHeight: true
                color: App.Theme.surface
                radius: 15

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 62
                        spacing: 11
                        Rectangle {
                            width: 36
                            height: 36
                            radius: 11
                            gradient: Gradient {
                                GradientStop { position: 0; color: App.Theme.cyan }
                                GradientStop { position: 1; color: App.Theme.violet }
                            }
                            Text {
                                anchors.centerIn: parent
                                text: "D"
                                color: App.Theme.canvas
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 17
                                font.bold: true
                            }
                        }
                        Column {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                text: "DDL REMINDER"
                                color: App.Theme.textPrimary
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 14
                                font.weight: Font.Bold
                                font.letterSpacing: 0.8
                            }
                            Text {
                                text: "FOCUS CONSOLE"
                                color: App.Theme.cyan
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 9
                                font.letterSpacing: 1.4
                            }
                        }
                    }

                    Text {
                        text: "任务视图"
                        color: App.Theme.textMuted
                        font.family: App.Theme.fontFamily
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        leftPadding: 10
                        topPadding: 16
                        bottomPadding: 4
                    }

                    NavigationButton {
                        Layout.fillWidth: true
                        text: "进行中"
                        iconText: "◉"
                        selected: appController.currentFilter === "active"
                        onSelectedRequested: appController.setFilter("active")
                    }
                    NavigationButton {
                        Layout.fillWidth: true
                        text: "即将截止"
                        iconText: "⌁"
                        selected: appController.currentFilter === "urgent"
                        onSelectedRequested: appController.setFilter("urgent")
                    }
                    NavigationButton {
                        Layout.fillWidth: true
                        text: "已完成"
                        iconText: "✓"
                        selected: appController.currentFilter === "completed"
                        onSelectedRequested: appController.setFilter("completed")
                    }

                    Item { Layout.fillHeight: true }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 74
                        radius: App.Theme.radiusMedium
                        color: "#0B1B2A"
                        border.color: "#173A52"
                        Column {
                            anchors.left: parent.left
                            anchors.leftMargin: 14
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 5
                            Text {
                                text: "本地优先"
                                color: App.Theme.textPrimary
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                            }
                            Text {
                                text: "数据仅保存在此设备"
                                color: App.Theme.textMuted
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 10
                            }
                        }
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 64

                        MouseArea {
                            anchors.fill: parent
                            anchors.rightMargin: 132
                            onPressed: root.startSystemMove()
                        }

                        Row {
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            WindowButton { text: "—"; onClicked: root.showMinimized() }
                            WindowButton {
                                text: root.visibility === Window.Maximized ? "❐" : "□"
                                onClicked: root.visibility === Window.Maximized
                                           ? root.showNormal() : root.showMaximized()
                            }
                            WindowButton { text: "×"; destructive: true; onClicked: root.hide() }
                        }
                    }

                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.leftMargin: 42
                        Layout.rightMargin: 42
                        Layout.bottomMargin: 34

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 20

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 18
                                Column {
                                    Layout.fillWidth: true
                                    spacing: 5
                                    Text {
                                        text: appController.sectionTitle
                                        color: App.Theme.textPrimary
                                        font.family: App.Theme.fontFamily
                                        font.pixelSize: 28
                                        font.weight: Font.Bold
                                    }
                                    Text {
                                        text: appController.sectionCount + " 项任务 · 按截止时间排列"
                                        color: App.Theme.textMuted
                                        font.family: App.Theme.fontFamily
                                        font.pixelSize: 12
                                    }
                                }
                                AppButton {
                                    id: createTaskButton
                                    objectName: "createTaskButton"
                                    text: "+  新建任务"
                                    primary: true
                                }
                            }

                            TextField {
                                id: searchField
                                objectName: "searchField"
                                Layout.fillWidth: true
                                Layout.preferredHeight: 46
                                placeholderText: "搜索标题或描述"
                                color: App.Theme.textPrimary
                                placeholderTextColor: App.Theme.textMuted
                                font.family: App.Theme.fontFamily
                                font.pixelSize: 13
                                leftPadding: 18
                                rightPadding: 18
                                selectByMouse: true
                                onTextChanged: appController.setSearchQuery(text)
                                background: Rectangle {
                                    radius: App.Theme.radiusMedium
                                    color: App.Theme.surface
                                    border.color: searchField.activeFocus
                                                  ? App.Theme.cyan : App.Theme.borderSoft
                                    border.width: 1
                                }
                            }

                            ListView {
                                id: taskList
                                objectName: "taskList"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 12
                                clip: true
                                model: appController.mainModel
                                boundsBehavior: Flickable.StopAtBounds
                                ScrollBar.vertical: ScrollBar {}

                                delegate: TaskCard {
                                    width: taskList.width - (taskList.ScrollBar.vertical.visible ? 12 : 0)
                                    taskId: model.taskId
                                    title: model.title
                                    description: model.description
                                    deadlineText: model.deadlineText
                                    remainingText: model.remainingText
                                    category: model.category
                                    completed: model.completed
                                    onCompleteRequested: appController.completeTask(taskId)
                                }

                                Text {
                                    anchors.centerIn: parent
                                    visible: taskList.count === 0
                                    text: "这里很安静\n创建一个任务，开始专注下一件事"
                                    color: App.Theme.textMuted
                                    horizontalAlignment: Text.AlignHCenter
                                    lineHeight: 1.5
                                    font.family: App.Theme.fontFamily
                                    font.pixelSize: 14
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
